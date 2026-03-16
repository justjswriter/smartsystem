from datetime import datetime

from pydantic import BaseModel


class DashboardPoint(BaseModel):
    recorded_at: datetime
    moisture: float | None
    temperature: float | None
    humidity: float | None
    light: float | None


class DashboardResponse(BaseModel):
    plant_id: int
    last_updated_at: datetime | None
    current: DashboardPoint | None
    history: list[DashboardPoint]
