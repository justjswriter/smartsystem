from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PlantSummaryItem(BaseModel):
    plant_id: int
    name: str
    latest_soil: Optional[float] = None
    latest_temp: Optional[float] = None
    latest_humidity: Optional[float] = None
    latest_light: Optional[float] = None
    last_seen: Optional[datetime] = None
    health_status: str


class DashboardSummaryOut(BaseModel):
    plants_total: int
    plants_active: int
    open_alerts: int
    plants: List[PlantSummaryItem]


class SensorCardOut(BaseModel):
    soil_moisture_percent: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light_percent: Optional[float] = None
    recorded_at: Optional[datetime] = None
    health_status: str
    # Explainability: which thresholds failed on last sample (empty if normal)
    abnormal_codes: List[str] = Field(default_factory=list)


class PlantDashboardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plant_id: int
    plant_name: str
    latest: Optional[SensorCardOut] = None
    recent_readings_count: int = 0
    open_alerts: int = 0
