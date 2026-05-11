from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import NotificationSeverity, NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: NotificationType
    severity: NotificationSeverity
    title_key: str
    message_key: str
    params: dict | None
    title: str | None
    message: str | None
    related_plant_id: int | None
    related_alert_id: int | None
    related_sensor_id: int | None
    dedupe_key: str | None
    read_at: datetime | None
    created_at: datetime
