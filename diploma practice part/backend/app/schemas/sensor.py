from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.sensor import SensorStatus, SensorType


class SensorCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    plant_id: Optional[int] = None
    sensor_type: SensorType = SensorType.multi
    status: SensorStatus = SensorStatus.offline


class SensorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    plant_id: Optional[int] = None
    device_id: str
    sensor_type: str
    status: str
    created_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
