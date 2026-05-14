from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class NotificationSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_email: EmailStr | None
    email_enabled: bool
    critical_only: bool
    email_critical_alerts: bool
    email_moisture_alerts: bool
    email_temperature_alerts: bool
    email_humidity_alerts: bool
    email_light_alerts: bool
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime


class NotificationSettingsUpdate(BaseModel):
    notification_email: EmailStr | None = None
    email_enabled: bool | None = None
    critical_only: bool | None = None
    email_critical_alerts: bool | None = None
    email_moisture_alerts: bool | None = None
    email_temperature_alerts: bool | None = None
    email_humidity_alerts: bool | None = None
    email_light_alerts: bool | None = None


class TestEmailResponse(BaseModel):
    status: str
    detail: str
