from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.application.schemas.notification_settings import NotificationSettingsUpdate
from app.application.services.email_service import EmailSendResult
from app.application.services.notification_settings_service import NotificationSettingsService


class FakeSettingsRepository:
    def __init__(self, settings=None):
        self.settings = settings

    async def get_or_create_for_user(self, user_id):
        if self.settings is None:
            now = datetime.now(timezone.utc)
            self.settings = make_settings(
                user_id=user_id,
                notification_email=None,
                email_enabled=False,
                critical_only=True,
                created_at=now,
                updated_at=now,
            )
        return self.settings

    async def update_for_user(self, *, user_id, values):
        settings = await self.get_or_create_for_user(user_id)
        for key, value in values.items():
            setattr(settings, key, value)
        settings.updated_at = datetime.now(timezone.utc)
        return settings


class FakeEmailService:
    def __init__(self, result=None):
        self.result = result or EmailSendResult(status="logged", detail="SMTP is not configured; email was logged only.")
        self.sent_to = []

    def send_test_email(self, *, to_email):
        self.sent_to.append(to_email)
        return self.result


def make_settings(**overrides):
    now = datetime.now(timezone.utc)
    values = {
        "id": 1,
        "user_id": 10,
        "notification_email": None,
        "email_enabled": False,
        "critical_only": True,
        "email_critical_alerts": True,
        "email_moisture_alerts": True,
        "email_temperature_alerts": True,
        "email_humidity_alerts": True,
        "email_light_alerts": True,
        "verified_at": None,
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return type("Settings", (), values)()


def make_service(settings=None, email_service=None):
    service = NotificationSettingsService.__new__(NotificationSettingsService)
    service.settings_repo = FakeSettingsRepository(settings)
    service.email_service = email_service or FakeEmailService()
    return service


@pytest.mark.asyncio
async def test_default_notification_settings_returned():
    service = make_service()

    settings = await service.get_for_user(user_id=25)

    assert settings.user_id == 25
    assert settings.notification_email is None
    assert settings.email_enabled is False
    assert settings.critical_only is True
    assert settings.email_light_alerts is True


@pytest.mark.asyncio
async def test_patch_updates_notification_settings():
    service = make_service(make_settings(user_id=10))
    payload = NotificationSettingsUpdate(
        notification_email="plant-owner@example.com",
        email_enabled=True,
        critical_only=False,
        email_light_alerts=False,
        email_moisture_alerts=True,
    )

    settings = await service.update_for_user(user_id=10, payload=payload)

    assert settings.notification_email == "plant-owner@example.com"
    assert settings.email_enabled is True
    assert settings.critical_only is False
    assert settings.email_light_alerts is False
    assert settings.email_moisture_alerts is True


def test_invalid_notification_email_rejected():
    with pytest.raises(ValidationError):
        NotificationSettingsUpdate(notification_email="not-an-email")


@pytest.mark.asyncio
async def test_test_email_returns_logged_status_with_mocked_sender():
    email_service = FakeEmailService()
    service = make_service(make_settings(notification_email="demo@example.com"), email_service)

    result = await service.send_test_email(user_id=10)

    assert result.status == "logged"
    assert email_service.sent_to == ["demo@example.com"]
