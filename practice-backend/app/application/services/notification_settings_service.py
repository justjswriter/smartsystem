from __future__ import annotations

from app.application.schemas.notification_settings import NotificationSettingsUpdate
from app.application.services.email_service import EmailService, EmailSendResult
from app.infrastructure.repositories import NotificationSettingsRepository


class NotificationSettingsService:
    def __init__(self, db):
        self.settings_repo = NotificationSettingsRepository(db)
        self.email_service = EmailService()

    async def get_for_user(self, *, user_id: int):
        return await self.settings_repo.get_or_create_for_user(user_id)

    async def update_for_user(self, *, user_id: int, payload: NotificationSettingsUpdate):
        values = {
            field: getattr(payload, field)
            for field in payload.model_fields_set
            if field in {"notification_email", "email_enabled", "critical_only"}
        }
        if values.get("notification_email") is not None:
            values["notification_email"] = str(values["notification_email"])
        return await self.settings_repo.update_for_user(user_id=user_id, values=values)

    async def send_test_email(self, *, user_id: int) -> EmailSendResult:
        settings = await self.settings_repo.get_or_create_for_user(user_id)
        if not settings.notification_email:
            return EmailSendResult(status="missing_email", detail="Notification email is not set.")
        return self.email_service.send_test_email(to_email=settings.notification_email)
