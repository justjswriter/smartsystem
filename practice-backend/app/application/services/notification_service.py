import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AlertSeverity, NotificationSeverity, NotificationType
from app.infrastructure.models import Alert
from app.application.services.email_service import EmailService
from app.infrastructure.repositories import NotificationRepository, NotificationSettingsRepository
from app.infrastructure.services.event_bus import event_bus

logger = logging.getLogger(__name__)


class NotificationService:
    DEDUPE_WINDOW = timedelta(minutes=5)

    def __init__(self, db: AsyncSession):
        self.notification_repo = NotificationRepository(db)
        self.notification_settings_repo = NotificationSettingsRepository(db)
        self.email_service = EmailService()

    @staticmethod
    def _notification_severity(alert_severity: AlertSeverity) -> NotificationSeverity:
        if alert_severity == AlertSeverity.CRITICAL:
            return NotificationSeverity.CRITICAL
        if alert_severity in (AlertSeverity.HIGH, AlertSeverity.MEDIUM):
            return NotificationSeverity.WARNING
        return NotificationSeverity.INFO

    @staticmethod
    def _notification_type(alert_severity: AlertSeverity) -> NotificationType:
        if alert_severity == AlertSeverity.CRITICAL:
            return NotificationType.CRITICAL_ALERT
        return NotificationType.PLANT_CONDITION

    async def create_once(self, *, payload: dict):
        dedupe_key = payload.get("dedupe_key")
        user_id = payload["user_id"]
        if dedupe_key:
            existing = await self.notification_repo.find_recent_by_dedupe_key(
                user_id=user_id,
                dedupe_key=dedupe_key,
                created_after=datetime.now(timezone.utc) - self.DEDUPE_WINDOW,
            )
            if existing:
                return existing, False

        notification = await self.notification_repo.create(payload)
        await event_bus.publish(
            f"notifications:{user_id}",
            {
                "event": "notification_created",
                "notification_id": notification.id,
                "type": notification.type.value,
                "severity": notification.severity.value,
            },
        )
        await self._send_email_if_enabled(notification)
        return notification, True

    async def _send_email_if_enabled(self, notification) -> None:
        try:
            settings = await self.notification_settings_repo.get_by_user_id(notification.user_id)
            if not settings or not settings.email_enabled or not settings.notification_email:
                return
            if not self._passes_email_preferences(settings, notification):
                return
            if settings.critical_only and not self._passes_critical_only(notification):
                return
            self.email_service.send_notification_email(
                to_email=settings.notification_email,
                notification=notification,
            )
        except Exception:
            logger.exception("Email notification channel failed for notification_id=%s", notification.id)

    @staticmethod
    def _passes_email_preferences(settings, notification) -> bool:
        raw_params = getattr(notification, "params", None)
        params = raw_params if isinstance(raw_params, dict) else {}
        metric = str(params.get("metric", "")).lower()
        if notification.severity == NotificationSeverity.CRITICAL:
            return bool(getattr(settings, "email_critical_alerts", True))
        if metric == "moisture":
            return bool(getattr(settings, "email_moisture_alerts", True))
        if metric == "temperature":
            return bool(getattr(settings, "email_temperature_alerts", True))
        if metric == "humidity":
            return bool(getattr(settings, "email_humidity_alerts", True))
        if metric == "light":
            return bool(getattr(settings, "email_light_alerts", True))
        return True

    @staticmethod
    def _passes_critical_only(notification) -> bool:
        if notification.severity == NotificationSeverity.CRITICAL:
            return True
        raw_params = getattr(notification, "params", None)
        params = raw_params if isinstance(raw_params, dict) else {}
        if params.get("issue") == "low_light":
            return True
        return str(params.get("severity", "")).lower() in {"high", "critical"}

    async def create_for_alert(self, *, alert: Alert, issue_code: str | None = None):
        notification_type = self._notification_type(alert.severity)
        severity = self._notification_severity(alert.severity)
        title_key = (
            "notification.alert.critical.title"
            if notification_type == NotificationType.CRITICAL_ALERT
            else "notification.alert.condition.title"
        )
        message_key = (
            "notification.alert.critical.message"
            if notification_type == NotificationType.CRITICAL_ALERT
            else "notification.alert.condition.message"
        )
        metric = alert.metric or "unknown"
        threshold = getattr(alert, "threshold", None)
        threshold_part = "none" if threshold is None else f"{float(threshold):g}"
        return await self.create_once(
            payload={
                "user_id": alert.user_id,
                "type": notification_type,
                "severity": severity,
                "title_key": title_key,
                "message_key": message_key,
                "params": {
                    "plant_id": alert.plant_id,
                    "plant_name": getattr(getattr(alert, "plant", None), "name", None),
                    "alert_id": alert.id,
                    "metric": metric,
                    "severity": alert.severity.value,
                    "issue": issue_code,
                },
                "title": (
                    f"Critical alert for {alert.plant.name}"
                    if notification_type == NotificationType.CRITICAL_ALERT and getattr(alert, "plant", None)
                    else "Critical plant alert"
                    if notification_type == NotificationType.CRITICAL_ALERT
                    else f"{alert.plant.name} needs attention"
                    if getattr(alert, "plant", None)
                    else "Plant needs attention"
                ),
                "message": (
                    f"A critical {metric} issue was detected for {alert.plant.name}. Check the plant in the web app."
                    if notification_type == NotificationType.CRITICAL_ALERT and getattr(alert, "plant", None)
                    else f"A critical {metric} issue was detected. Check the plant in the web app."
                    if notification_type == NotificationType.CRITICAL_ALERT
                    else f"A {metric} issue was detected for {alert.plant.name}. Open the plant in the web app for details."
                    if getattr(alert, "plant", None)
                    else f"A {metric} issue was detected. Open the plant in the web app for details."
                ),
                "related_plant_id": alert.plant_id,
                "related_alert_id": alert.id,
                "related_sensor_id": alert.sensor_id,
                "dedupe_key": f"alert:{alert.plant_id}:{metric}:{issue_code or 'generic'}:{threshold_part}",
            }
        )

    async def list_for_user(self, *, user_id: int, unread_only: bool, limit: int, offset: int):
        return await self.notification_repo.list_for_user(
            user_id=user_id, unread_only=unread_only, limit=limit, offset=offset
        )

    async def mark_read(self, *, user_id: int, notification_id: int):
        notification = await self.notification_repo.get_for_user(
            user_id=user_id, notification_id=notification_id
        )
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notification = await self.notification_repo.mark_read(notification)
        await event_bus.publish(
            f"notifications:{user_id}",
            {"event": "notification_read", "notification_id": notification.id},
        )
        return notification

    async def mark_all_read(self, *, user_id: int):
        notifications = await self.notification_repo.mark_all_read(user_id=user_id)
        await event_bus.publish(
            f"notifications:{user_id}",
            {"event": "notifications_read_all", "count": len(notifications)},
        )
        return notifications
