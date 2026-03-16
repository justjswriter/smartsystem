from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import SensorStatus, SensorType


class SensorCreate(BaseModel):
    device_id: str = Field(min_length=3, max_length=255)
    type: SensorType = SensorType.MULTI


class SensorAttachRequest(BaseModel):
    plant_id: int


class SensorResponse(BaseModel):
    id: int
    device_id: str
    type: SensorType
    status: SensorStatus
    plant_id: int | None
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorDataIngest(BaseModel):
    moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    light: float | None = None
    recorded_at: datetime | None = None
