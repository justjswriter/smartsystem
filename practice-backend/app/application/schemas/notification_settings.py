from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class NotificationSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_email: EmailStr | None
    email_enabled: bool
    critical_only: bool
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime


class NotificationSettingsUpdate(BaseModel):
    notification_email: EmailStr | None = None
    email_enabled: bool | None = None
    critical_only: bool | None = None


class TestEmailResponse(BaseModel):
    status: str
    detail: str
