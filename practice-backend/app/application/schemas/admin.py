from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.enums import AlertStatus, SensorStatus, UserRole


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class AdminSensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    device_id: str
    status: SensorStatus
    plant_id: int | None
    last_seen_at: datetime | None
    last_ingest_source: str | None
    last_error_at: datetime | None
    last_error_message: str | None
    created_at: datetime


class AdminPlantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    species: str | None
    location: str | None
    created_at: datetime


class AdminAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    user_id: int
    status: AlertStatus
    title: str
    created_at: datetime


class SystemLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    event_type: str
    message: str
    payload: dict | None
    created_at: datetime

