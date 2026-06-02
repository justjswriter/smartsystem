from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.health_rules import build_alert_message, evaluate_reading
from app.domain.percent_conversion import light_raw_to_percent, soil_moisture_raw_to_percent
from app.domain.recommendation_text import build_recommendation_text
from app.models.alert import Alert, AlertStatus
from app.models.recommendation import Recommendation
from app.models.user import User
from app.models.sensor import Sensor, SensorStatus
from app.repositories.plant_repository import PlantRepository
from app.repositories.reading_repository import ReadingRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.sensor_repository import SensorRepository
from app.schemas.reading import (
    IngestRequest,
    IngestResponse,
    ReadingOut,
    AlertBriefOut,
    RecommendationOut,
)
from app.schemas.reading import ReadingListItem


def _health_label(abnormal_count: int) -> str:
    if abnormal_count == 0:
        return "normal"
    if abnormal_count == 1:
        return "warning"
    return "critical"


def resolve_or_create_sensor(
    db: Session, device_id: str, plant_id: int
) -> Tuple[Sensor, bool]:
    """
    Returns (sensor, created_new). New sensors are only created if ALLOW_AUTO_REGISTER_DEVICE is on.
    """
    settings = get_settings()
    s_repo = SensorRepository(db)
    sensor = s_repo.get_by_device_id(device_id)
    if sensor is None:
        if not settings.ALLOW_AUTO_REGISTER_DEVICE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown device_id; enable ALLOW_AUTO_REGISTER_DEVICE to auto-provision",
            )
        sensor = s_repo.create(
            device_id=device_id,
            plant_id=plant_id,
            commit=False,
        )
        return sensor, True
    if sensor.plant_id is None:
        sensor.plant_id = plant_id
    elif sensor.plant_id != plant_id:
        raise HTTPException(
            status_code=400,
            detail="device_id is registered to a different plant; update or detach the sensor first",
        )
    return sensor, False


def ingest_reading(db: Session, data: IngestRequest) -> IngestResponse:
    """
    End-to-end IoT ingest: validate plant, link sensor, persist reading, then rule-based
    alert + recommendation in one transaction.
    """
    settings = get_settings()
    p_repo = PlantRepository(db)
    plant = p_repo.get_by_id(data.plant_id)
    if not plant or not plant.is_active:
        raise HTTPException(
            status_code=404, detail="Plant not found"
        )
    s_repo = SensorRepository(db)
    r_repo = ReadingRepository(db)
    a_repo = AlertRepository(db)
    m_repo = RecommendationRepository(db)

    sensor, _ = resolve_or_create_sensor(db, data.device_id, data.plant_id)
    m_pct = soil_moisture_raw_to_percent(data.soil_moisture_raw, settings)
    l_pct = light_raw_to_percent(data.light_raw, settings)

    now = datetime.now(timezone.utc)
    sensor.status = SensorStatus.online
    sensor.last_seen_at = now
    s_repo.save(sensor, commit=False)

    reading = r_repo.create(
        plant_id=data.plant_id,
        sensor_id=sensor.id,
        device_id=data.device_id,
        soil_moisture_raw=data.soil_moisture_raw,
        soil_moisture_percent=m_pct,
        temperature=data.temperature,
        humidity=data.humidity,
        light_raw=data.light_raw,
        light_percent=l_pct,
        commit=False,
    )

    items, sev = evaluate_reading(
        m_pct, data.temperature, data.humidity, l_pct, settings
    )
    health = _health_label(len(items))

    alert: Optional[Alert] = None
    rec: Optional[Recommendation] = None
    if items:
        msg = build_alert_message(items)
        alert = a_repo.create(
            plant_id=data.plant_id,
            alert_type="threshold_breach",
            severity=sev,
            message=msg,
            status=AlertStatus.created,
            commit=False,
        )
        t_text, expl = build_recommendation_text(items)
        rec = m_repo.create(
            plant_id=data.plant_id,
            text=t_text,
            explanation=expl,
            alert_id=alert.id,
            commit=False,
        )

    db.commit()
    for obj in (reading, alert, rec, sensor):
        if obj is not None:
            db.refresh(obj)

    out_reading = ReadingOut.model_validate(reading)
    out_alert: Optional[AlertBriefOut] = None
    if alert:
        out_alert = AlertBriefOut(
            id=alert.id,
            type=alert.type,
            severity=alert.severity.value,  # type: ignore[union-attr]
            message=alert.message,
            status=alert.status.value,  # type: ignore[union-attr]
            created_at=alert.created_at,
        )
    out_rec: Optional[RecommendationOut] = None
    if rec:
        out_rec = RecommendationOut(
            id=rec.id,
            text=rec.text,
            explanation=rec.explanation,
            created_at=rec.created_at,
        )
    return IngestResponse(
        reading=out_reading,
        alert=out_alert,
        recommendation=out_rec,
        health_status=health,
    )


def list_readings(
    db: Session, user: User, plant_id: int, limit: int, offset: int
) -> List[ReadingListItem]:
    from app.services import plant_service
    plant_service.get_plant_entity_for_user(db, user, plant_id, allow_inactive=False)
    rows = ReadingRepository(db).list_by_plant(plant_id, limit=limit, offset=offset)
    return [ReadingListItem.model_validate(r) for r in rows]


def get_latest(
    db: Session, user: User, plant_id: int
) -> ReadingOut:
    from app.services import plant_service
    plant_service.get_plant_entity_for_user(db, user, plant_id, allow_inactive=False)
    r = ReadingRepository(db).latest_for_plant(plant_id)
    if not r:
        raise HTTPException(status_code=404, detail="No readings for this plant yet")
    return ReadingOut.model_validate(r)
