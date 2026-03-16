from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.recommendation_service import RecommendationService
from app.core.config import settings
from app.domain.enums import AlertSeverity, AlertStatus
from app.infrastructure.repositories import (
    AlertRepository,
    PlantRepository,
    SensorDataRepository,
    SensorRepository,
    SystemLogRepository,
)
from app.infrastructure.services.event_bus import event_bus


class AlertService:
    def __init__(self, db: AsyncSession):
        self.alert_repo = AlertRepository(db)
        self.sensor_repo = SensorRepository(db)
        self.plant_repo = PlantRepository(db)
        self.sensor_data_repo = SensorDataRepository(db)
        self.recommendation_service = RecommendationService(db)
        self.log_repo = SystemLogRepository(db)

    @staticmethod
    def _severity_from_ratio(ratio: float) -> AlertSeverity:
        if ratio >= 2:
            return AlertSeverity.CRITICAL
        if ratio >= 1.5:
            return AlertSeverity.HIGH
        if ratio >= 1.2:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW

    async def ingest_sensor_data(self, *, device_id: str, payload: dict):
        sensor = await self.sensor_repo.get_by_device_id(device_id)
        if not sensor:
            raise ValueError("Sensor not found")
        if not sensor.plant_id:
            raise ValueError("Sensor is not attached to any plant")

        data = await self.sensor_data_repo.create(
            sensor_id=sensor.id,
            plant_id=sensor.plant_id,
            payload=payload,
        )
        await self.sensor_repo.touch_seen(sensor)
        await self._evaluate_thresholds(sensor_id=sensor.id, plant_id=sensor.plant_id, payload=payload)
        await event_bus.publish(
            f"dashboard:{sensor.plant_id}",
            {
                "event": "sensor_data",
                "plant_id": sensor.plant_id,
                "sensor_id": sensor.id,
                "data": {
                    "moisture": payload.get("moisture"),
                    "temperature": payload.get("temperature"),
                    "humidity": payload.get("humidity"),
                    "light": payload.get("light"),
                    "recorded_at": (payload.get("recorded_at") or datetime.now(timezone.utc)).isoformat(),
                },
            },
        )
        return data

    async def _evaluate_thresholds(self, *, sensor_id: int, plant_id: int, payload: dict) -> None:
        checks: list[tuple[str, float, float, str]] = []
        moisture = payload.get("moisture")
        temperature = payload.get("temperature")
        humidity = payload.get("humidity")
        light = payload.get("light")

        if moisture is not None and moisture < settings.MOISTURE_MIN:
            checks.append(("moisture", moisture, settings.MOISTURE_MIN, "below"))
        if temperature is not None and temperature > settings.TEMPERATURE_MAX:
            checks.append(("temperature", temperature, settings.TEMPERATURE_MAX, "above"))
        if humidity is not None and humidity < settings.HUMIDITY_MIN:
            checks.append(("humidity", humidity, settings.HUMIDITY_MIN, "below"))
        if light is not None and light < settings.LIGHT_MIN:
            checks.append(("light", light, settings.LIGHT_MIN, "below"))

        plant = await self.plant_repo.get_by_id(plant_id)
        if not plant:
            return

        for metric, value, threshold, direction in checks:
            existing = await self.alert_repo.find_open_by_metric(plant_id=plant_id, metric=metric)
            if existing:
                continue
            ratio = (threshold / value) if direction == "below" and value > 0 else (value / threshold)
            severity = self._severity_from_ratio(ratio)
            alert = await self.alert_repo.create(
                {
                    "user_id": plant.user_id,
                    "plant_id": plant_id,
                    "sensor_id": sensor_id,
                    "status": AlertStatus.CREATED,
                    "severity": severity,
                    "title": f"{metric.capitalize()} threshold {direction}",
                    "message": f"{metric.capitalize()} is {direction} threshold",
                    "metric": metric,
                    "value": value,
                    "threshold": threshold,
                }
            )
            await self.alert_repo.add_transition(
                alert_id=alert.id,
                from_status=AlertStatus.CREATED,
                to_status=AlertStatus.CREATED,
                user_id=plant.user_id,
                note="Alert created from ingest evaluation",
            )
            await self.recommendation_service.create_for_alert(
                plant_id=plant_id, alert_id=alert.id, metric=metric, severity=severity.value
            )
            await self.log_repo.create(
                event_type="alert_created",
                message=f"Alert {alert.id} created for plant {plant_id}",
                user_id=plant.user_id,
                payload={"alert_id": alert.id, "metric": metric, "value": value},
            )
            await event_bus.publish(
                f"alerts:{plant.user_id}",
                {"event": "new_alert", "alert_id": alert.id, "metric": metric, "severity": severity.value},
            )
