from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.health_rules import evaluate_reading
from app.models.user import User
from app.repositories.plant_repository import PlantRepository
from app.repositories.reading_repository import ReadingRepository
from app.repositories.alert_repository import AlertRepository
from app.schemas.dashboard import (
    DashboardSummaryOut,
    PlantDashboardOut,
    PlantSummaryItem,
    SensorCardOut,
)
from app.services import plant_service


def _label_from_abcount(n: int) -> str:
    if n == 0:
        return "normal"
    if n == 1:
        return "warning"
    return "critical"


def get_dashboard_summary(db: Session, user: User) -> DashboardSummaryOut:
    settings = get_settings()
    p_repo = PlantRepository(db)
    a_repo = AlertRepository(db)
    r_repo = ReadingRepository(db)
    plants = p_repo.list_for_user(user.id, only_active=True)
    open_n = a_repo.count_open_for_user(user.id)
    items: List[PlantSummaryItem] = []
    for p in plants:
        last = r_repo.latest_for_plant(p.id)
        h = "normal"
        last_ts: Optional[datetime] = last.recorded_at if last else None
        if last:
            items_ev, _ = evaluate_reading(
                last.soil_moisture_percent,
                last.temperature,
                last.humidity,
                last.light_percent,
                settings,
            )
            h = _label_from_abcount(len(items_ev))
        items.append(
            PlantSummaryItem(
                plant_id=p.id,
                name=p.name,
                latest_soil=last.soil_moisture_percent if last else None,
                latest_temp=last.temperature if last else None,
                latest_humidity=last.humidity if last else None,
                latest_light=last.light_percent if last else None,
                last_seen=last_ts,
                health_status=h,
            )
        )
    return DashboardSummaryOut(
        plants_total=len(plants),
        plants_active=len([x for x in plants if x.is_active]),
        open_alerts=open_n,
        plants=items,
    )


def get_plant_dashboard(db: Session, user: User, plant_id: int) -> PlantDashboardOut:
    settings = get_settings()
    p = plant_service.get_plant_entity_for_user(db, user, plant_id, allow_inactive=False)
    r_repo = ReadingRepository(db)
    a_repo = AlertRepository(db)
    last = r_repo.latest_for_plant(plant_id)
    codes: List[str] = []
    h = "normal"
    if last:
        ev_items, _ = evaluate_reading(
            last.soil_moisture_percent,
            last.temperature,
            last.humidity,
            last.light_percent,
            settings,
        )
        h = _label_from_abcount(len(ev_items))
        codes = [e.code for e in ev_items]
    open_alerts = len(a_repo.list_open_for_plant(plant_id))
    n_readings = r_repo.count_for_plant(plant_id)
    card = None
    if last:
        card = SensorCardOut(
            soil_moisture_percent=last.soil_moisture_percent,
            temperature=last.temperature,
            humidity=last.humidity,
            light_percent=last.light_percent,
            recorded_at=last.recorded_at,
            health_status=h,
            abnormal_codes=codes,
        )
    return PlantDashboardOut(
        plant_id=p.id,
        plant_name=p.name,
        latest=card,
        recent_readings_count=n_readings,
        open_alerts=open_alerts,
    )
