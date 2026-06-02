from datetime import datetime

from pydantic import BaseModel, Field
from pydantic import ConfigDict

from app.domain.enums import SensorStatus, SensorType


class SensorCreate(BaseModel):
    device_id: str = Field(min_length=3, max_length=255)
    type: SensorType = SensorType.MULTI


class SensorAttachRequest(BaseModel):
    plant_id: int


class SensorAssignRequest(BaseModel):
    user_id: int


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    device_id: str
    type: SensorType
    status: SensorStatus
    plant_id: int | None
    is_active: bool
    last_seen_at: datetime | None
    last_ingest_source: str | None
    last_error_at: datetime | None
    last_error_message: str | None
    created_at: datetime
    updated_at: datetime

class SensorProvisionResponse(BaseModel):
    sensor: SensorResponse
    device_token: str


class SensorDataIngest(BaseModel):
    moisture: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    light: float | None = None
    recorded_at: datetime | None = None
