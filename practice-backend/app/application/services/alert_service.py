from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.notification_service import NotificationService
from app.application.services.recommendation_service import RecommendationService
from app.core.security import verify_device_token
from app.domain.enums import AlertSeverity, AlertStatus, SensorStatus
from app.domain.plant_knowledge import resolve_plant_profile
from app.domain.plant_knowledge.types import IssueDefinition
from app.infrastructure.repositories import (
    AlertRepository,
    PlantRepository,
    SensorDataRepository,
    SensorRepository,
    SystemLogRepository,
)
from app.infrastructure.services.event_bus import event_bus


class AlertService:
    LOCAL_TIME_OFFSET = timedelta(hours=5)
    NIGHT_START_HOUR = 20
    NIGHT_END_HOUR = 7
    SUSTAINED_HIGH_MOISTURE_WINDOW = timedelta(hours=48)
    SUSTAINED_HIGH_MOISTURE_MIN_SAMPLES = 3

    def __init__(self, db: AsyncSession):
        self.alert_repo = AlertRepository(db)
        self.sensor_repo = SensorRepository(db)
        self.plant_repo = PlantRepository(db)
        self.sensor_data_repo = SensorDataRepository(db)
        self.recommendation_service = RecommendationService(db)
        self.notification_service = NotificationService(db)
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

    async def ingest_sensor_data(self, *, device_id: str, device_token: str | None, source: str | None, payload: dict):
        sensor = await self.sensor_repo.get_by_device_id(device_id)
        if not sensor:
            raise ValueError("Sensor not found")
        if not device_token or not verify_device_token(device_token, sensor.device_token_hash):
            await self.sensor_repo.mark_error(sensor, "Invalid device token", source)
            await self.log_repo.create(
                event_type="ingest_auth_failed",
                message=f"Invalid ingest token for sensor {device_id}",
                user_id=sensor.user_id,
                payload={"sensor_id": sensor.id, "source": source},
            )
            raise PermissionError("Invalid device token")
        if not sensor.is_active or sensor.status == SensorStatus.DISABLED:
            await self.sensor_repo.mark_error(sensor, "Sensor is disabled or inactive", source)
            raise ValueError("Sensor is disabled or inactive")
        if not sensor.plant_id:
            await self.sensor_repo.mark_error(sensor, "Sensor is not attached to any plant", source)
            raise ValueError("Sensor is not attached to any plant")

        data = await self.sensor_data_repo.create(
            sensor_id=sensor.id,
            plant_id=sensor.plant_id,
            payload=payload,
        )
        await self.sensor_repo.touch_seen(sensor, source=source)
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
        plant = await self.plant_repo.get_by_id(plant_id)
        if not plant:
            return
        profile = resolve_plant_profile(getattr(plant, "species", None))
        checks = self._profile_checks(profile=profile, payload=payload)

        for issue, value in checks:
            existing = await self.alert_repo.find_open_by_metric_direction(
                plant_id=plant_id,
                metric=issue.metric,
                direction=issue.direction,
                threshold=issue.threshold,
            )
            if existing:
                continue
            if issue.code == "high_moisture" and not await self._is_sustained_high_moisture(
                plant_id=plant_id,
                threshold=issue.threshold,
                recorded_at=payload.get("recorded_at"),
            ):
                continue
            ratio = (issue.threshold / value) if issue.direction == "below" and value > 0 else (value / issue.threshold)
            severity = self._severity_from_ratio(ratio)
            alert = await self.alert_repo.create(
                {
                    "user_id": plant.user_id,
                    "plant_id": plant_id,
                    "sensor_id": sensor_id,
                    "status": AlertStatus.CREATED,
                    "severity": severity,
                    "title": issue.title.text("en"),
                    "message": issue.message.text("en"),
                    "metric": issue.metric,
                    "value": value,
                    "threshold": issue.threshold,
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
                plant_id=plant_id,
                alert_id=alert.id,
                metric=issue.metric,
                severity=severity.value,
                issue_code=issue.code,
                plant_profile=profile,
            )
            await self.notification_service.create_for_alert(alert=alert, issue_code=issue.code)
            await self.log_repo.create(
                event_type="alert_created",
                message=f"Alert {alert.id} created for plant {plant_id}",
                user_id=plant.user_id,
                payload={"alert_id": alert.id, "metric": issue.metric, "issue": issue.code, "value": value},
            )
            await event_bus.publish(
                f"alerts:{plant.user_id}",
                {"event": "new_alert", "alert_id": alert.id, "metric": issue.metric, "severity": severity.value},
            )

    @staticmethod
    def _profile_checks(*, profile, payload: dict) -> list[tuple[IssueDefinition, float]]:
        checks: list[tuple[IssueDefinition, float]] = []
        for issue in profile.issues.values():
            value = payload.get(issue.metric)
            if value is None:
                continue
            if issue.metric == "light" and issue.direction == "below" and AlertService._is_night(payload.get("recorded_at")):
                continue
            if issue.direction == "below" and value < issue.threshold:
                checks.append((issue, value))
            elif issue.direction == "above" and value > issue.threshold:
                checks.append((issue, value))
        return checks

    async def _is_sustained_high_moisture(
        self,
        *,
        plant_id: int,
        threshold: float,
        recorded_at: datetime | None,
    ) -> bool:
        history = await self.sensor_data_repo.history_for_plant(plant_id, 72)
        moisture_points = [
            item
            for item in history
            if getattr(item, "moisture", None) is not None and getattr(item, "recorded_at", None) is not None
        ]
        if len(moisture_points) < self.SUSTAINED_HIGH_MOISTURE_MIN_SAMPLES:
            return False

        current_time = recorded_at or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)

        last_normal_at: datetime | None = None
        for point in moisture_points:
            point_time = point.recorded_at
            if point_time.tzinfo is None:
                point_time = point_time.replace(tzinfo=timezone.utc)
            if float(point.moisture) <= threshold:
                last_normal_at = point_time

        sustained_points = []
        for point in moisture_points:
            point_time = point.recorded_at
            if point_time.tzinfo is None:
                point_time = point_time.replace(tzinfo=timezone.utc)
            if last_normal_at and point_time <= last_normal_at:
                continue
            if float(point.moisture) > threshold:
                sustained_points.append(point_time)

        if len(sustained_points) < self.SUSTAINED_HIGH_MOISTURE_MIN_SAMPLES:
            return False
        first_high_at = min(sustained_points)
        return current_time - first_high_at >= self.SUSTAINED_HIGH_MOISTURE_WINDOW

    @staticmethod
    def _is_night(recorded_at: datetime | None) -> bool:
        recorded = recorded_at or datetime.now(timezone.utc)
        if recorded.tzinfo is None:
            recorded = recorded.replace(tzinfo=timezone.utc)
        local_hour = (recorded.astimezone(timezone.utc) + AlertService.LOCAL_TIME_OFFSET).hour
        return local_hour >= AlertService.NIGHT_START_HOUR or local_hour < AlertService.NIGHT_END_HOUR
