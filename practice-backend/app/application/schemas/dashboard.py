from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlantConditionResponse(BaseModel):
    condition_status: str
    health_score: int | None
    risk_factors: list[str]
    confidence: float
    explanation: str


class RecommendationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    reason: str | None
    created_at: datetime


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
    condition: PlantConditionResponse
    active_recommendation: RecommendationSummary | None
