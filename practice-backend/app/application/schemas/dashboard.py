from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlantConditionResponse(BaseModel):
    condition_status: str
    health_score: int | None
    risk_factors: list[str]
    confidence: float
    explanation: str
    ml_prediction: str | None = None
    ml_confidence: float | None = None
    class_probabilities: dict[str, float] = Field(default_factory=dict)
    analysis_method: str = "rule_based"


class RecommendationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    text: str
    reason: str | None
    created_at: datetime | None = None
    metric: str | None = None
    severity: str | None = None
    source: str = "historical_alert"


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
