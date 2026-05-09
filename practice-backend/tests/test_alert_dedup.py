from types import SimpleNamespace

import pytest

from app.application.services.alert_service import AlertService


class FakeAlertRepository:
    def __init__(self, existing):
        self.existing = existing
        self.created = []

    async def find_open_by_metric(self, *, plant_id: int, metric: str):
        return self.existing

    async def create(self, payload: dict):
        self.created.append(payload)
        return SimpleNamespace(id=123)

    async def add_transition(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakePlantRepository:
    async def get_by_id(self, plant_id: int):
        return SimpleNamespace(id=plant_id, user_id=42)


class FakeRecommendationService:
    async def create_for_alert(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeLogRepository:
    async def create(self, **kwargs):
        return SimpleNamespace(**kwargs)


@pytest.mark.asyncio
async def test_active_metric_alert_is_not_duplicated():
    service = AlertService.__new__(AlertService)
    service.alert_repo = FakeAlertRepository(existing=SimpleNamespace(id=99))
    service.plant_repo = FakePlantRepository()
    service.recommendation_service = FakeRecommendationService()
    service.log_repo = FakeLogRepository()

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 10.0, "temperature": None, "humidity": None, "light": None},
    )

    assert service.alert_repo.created == []
