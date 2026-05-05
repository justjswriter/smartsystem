from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    plant_id: int
    soil_moisture_raw: int
    temperature: float
    humidity: float
    light_raw: int


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: Optional[int] = None
    sensor_id: Optional[int] = None
    device_id: str
    soil_moisture_raw: Optional[int] = None
    soil_moisture_percent: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light_raw: Optional[int] = None
    light_percent: Optional[float] = None
    recorded_at: Optional[datetime] = None


class AlertBriefOut(BaseModel):
    id: int
    type: str
    severity: str
    message: str
    status: str
    created_at: Optional[datetime] = None


class RecommendationOut(BaseModel):
    id: int
    text: str
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None


class IngestResponse(BaseModel):
    reading: ReadingOut
    alert: Optional[AlertBriefOut] = None
    recommendation: Optional[RecommendationOut] = None
    health_status: str  # normal, warning, critical (warning maps from medium or low-severity open issues)


class ReadingListItem(ReadingOut):
    pass
