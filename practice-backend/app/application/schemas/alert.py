from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import AlertSeverity, AlertStatus


class AlertResponse(BaseModel):
    id: int
    user_id: int
    plant_id: int
    sensor_id: int | None
    status: AlertStatus
    severity: AlertSeverity
    title: str
    message: str
    metric: str | None
    value: float | None
    threshold: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertTransitionRequest(BaseModel):
    to_status: AlertStatus
    note: str | None = None


class AlertTransitionResponse(BaseModel):
    id: int
    alert_id: int
    from_status: AlertStatus
    to_status: AlertStatus
    changed_by: int
    note: str | None
    changed_at: datetime

    class Config:
        from_attributes = True
