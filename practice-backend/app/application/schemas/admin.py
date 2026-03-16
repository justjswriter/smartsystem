from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.domain.enums import AlertStatus, SensorStatus, UserRole


class AdminUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminSensorResponse(BaseModel):
    id: int
    device_id: str
    status: SensorStatus
    plant_id: int | None
    last_seen_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAlertResponse(BaseModel):
    id: int
    plant_id: int
    user_id: int
    status: AlertStatus
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class SystemLogResponse(BaseModel):
    id: int
    user_id: int | None
    event_type: str
    message: str
    payload: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
