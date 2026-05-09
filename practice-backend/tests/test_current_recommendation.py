from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.application.schemas.dashboard import DashboardPoint
from app.application.services.monitoring_service import MonitoringService
from app.application.services.plant_condition_service import PlantConditionService
from app.application.services.recommendation_service import RecommendationService


def point(**overrides):
    payload = {
        "recorded_at": datetime.now(timezone.utc),
        "moisture": 45.0,
        "temperature": 24.0,
        "humidity": 45.0,
        "light": 500.0,
    }
    payload.update(overrides)
    return DashboardPoint(**payload)


def current_recommendation_for(current: DashboardPoint):
    condition = PlantConditionService().evaluate(current=current, history=[current])
    service = RecommendationService.__new__(RecommendationService)
    return service.build_current_recommendation(current=current, condition=condition)


def test_critical_low_moisture_beats_low_light():
    recommendation = current_recommendation_for(point(moisture=5.0, light=50.0))

    assert recommendation is not None
    assert recommendation.metric == "moisture"
    assert recommendation.severity == "critical"
    assert "watering" in recommendation.text.lower()
    assert recommendation.source == "current_condition"


def test_light_only_issue_returns_light_advice():
    recommendation = current_recommendation_for(point(light=50.0))

    assert recommendation is not None
    assert recommendation.metric == "light"
    assert "brighter" in recommendation.text.lower()


def test_stable_readings_return_stable_care_advice():
    recommendation = current_recommendation_for(point())

    assert recommendation is not None
    assert recommendation.id is None
    assert recommendation.created_at is None
    assert recommendation.metric == "stable"
    assert recommendation.severity == "normal"
    assert "stable" in recommendation.text.lower()


def test_normalized_readings_do_not_keep_historical_alert_advice():
    recommendation = current_recommendation_for(point(moisture=55.0, temperature=24.0, humidity=45.0, light=650.0))

    assert recommendation is not None
    assert recommendation.metric == "stable"
    assert "brighter" not in recommendation.text.lower()
    assert "watering" not in recommendation.text.lower()


class FakePlantRepository:
    async def get_for_user(self, plant_id: int, user_id: int):
        return SimpleNamespace(id=plant_id, user_id=user_id)


class FakeSensorDataRepository:
    def __init__(self, current: DashboardPoint):
        self.current = current

    async def latest_for_plant(self, plant_id: int):
        return self.current

    async def history_for_plant(self, plant_id: int, hours: int):
        return [self.current]


@pytest.mark.asyncio
async def test_dashboard_uses_current_reading_recommendation():
    service = MonitoringService.__new__(MonitoringService)
    service.plant_repo = FakePlantRepository()
    service.sensor_data_repo = FakeSensorDataRepository(point(moisture=5.0, light=50.0))
    service.condition_service = PlantConditionService()
    service.recommendation_service = RecommendationService.__new__(RecommendationService)

    dashboard = await service.get_dashboard(user_id=42, plant_id=7, hours=24)

    assert dashboard.active_recommendation is not None
    assert dashboard.active_recommendation.metric == "moisture"
