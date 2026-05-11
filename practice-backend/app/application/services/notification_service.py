from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AlertSeverity, NotificationSeverity, NotificationType
from app.infrastructure.models import Alert
from app.infrastructure.repositories import NotificationRepository
from app.infrastructure.services.event_bus import event_bus


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.notification_repo = NotificationRepository(db)

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
            existing = await self.notification_repo.find_unread_by_dedupe_key(
                user_id=user_id, dedupe_key=dedupe_key
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
        return notification, True

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
        return await self.create_once(
            payload={
                "user_id": alert.user_id,
                "type": notification_type,
                "severity": severity,
                "title_key": title_key,
                "message_key": message_key,
                "params": {
                    "plant_id": alert.plant_id,
                    "alert_id": alert.id,
                    "metric": metric,
                    "severity": alert.severity.value,
                    "issue": issue_code,
                },
                "title": alert.title,
                "message": alert.message,
                "related_plant_id": alert.plant_id,
                "related_alert_id": alert.id,
                "related_sensor_id": alert.sensor_id,
                "dedupe_key": f"alert:{alert.plant_id}:{metric}",
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
