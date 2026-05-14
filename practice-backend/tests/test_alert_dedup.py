from types import SimpleNamespace
from datetime import datetime, timedelta, timezone

import pytest

from app.application.services.alert_service import AlertService


class FakeAlertRepository:
    def __init__(self, existing):
        self.existing = existing
        self.created = []

    async def find_open_by_metric(self, *, plant_id: int, metric: str):
        return self.existing

    async def find_open_by_metric_direction(self, *, plant_id: int, metric: str, direction: str, threshold: float | None = None):
        if not self.existing:
            return None
        if self.existing.value is None or self.existing.threshold is None:
            return self.existing
        if threshold is not None and abs(float(self.existing.threshold) - float(threshold)) > 0.001:
            return None
        if direction == "below" and self.existing.value < self.existing.threshold:
            return self.existing
        if direction == "above" and self.existing.value > self.existing.threshold:
            return self.existing
        return None

    async def create(self, payload: dict):
        self.created.append(payload)
        return SimpleNamespace(id=123)

    async def add_transition(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakePlantRepository:
    async def get_by_id(self, plant_id: int):
        return SimpleNamespace(id=plant_id, user_id=42)


class FakeSensorDataRepository:
    def __init__(self, history=None):
        self.history = list(history or [])

    async def history_for_plant(self, plant_id: int, hours: int):
        return self.history


class FakeRecommendationService:
    async def create_for_alert(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeLogRepository:
    async def create(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeNotificationService:
    def __init__(self):
        self.alerts = []

    async def create_for_alert(self, *, alert, issue_code=None):
        self.alerts.append((alert, issue_code))
        return None, False


@pytest.mark.asyncio
async def test_active_metric_alert_is_not_duplicated():
    service = AlertService.__new__(AlertService)
    service.alert_repo = FakeAlertRepository(existing=SimpleNamespace(id=99, value=10.0, threshold=35.0))
    service.plant_repo = FakePlantRepository()
    service.recommendation_service = FakeRecommendationService()
    service.notification_service = FakeNotificationService()
    service.log_repo = FakeLogRepository()
    service.sensor_data_repo = FakeSensorDataRepository()

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 10.0, "temperature": None, "humidity": None, "light": None},
    )

    assert service.alert_repo.created == []
    assert service.notification_service.alerts == []


@pytest.mark.asyncio
async def test_opposite_metric_direction_creates_new_alert():
    service = AlertService.__new__(AlertService)
    service.alert_repo = FakeAlertRepository(existing=SimpleNamespace(id=99, value=10.0, threshold=35.0))
    service.plant_repo = FakePlantRepository()
    service.recommendation_service = FakeRecommendationService()
    service.notification_service = SimpleNamespace(create_for_alert=lambda **kwargs: None)
    service.log_repo = FakeLogRepository()

    async def create_for_alert(**kwargs):
        return SimpleNamespace(**kwargs)

    service.notification_service.create_for_alert = create_for_alert
    now = datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc)
    service.sensor_data_repo = FakeSensorDataRepository(
        [
            SimpleNamespace(moisture=90.0, recorded_at=now - timedelta(hours=50)),
            SimpleNamespace(moisture=92.0, recorded_at=now - timedelta(hours=24)),
            SimpleNamespace(moisture=100.0, recorded_at=now),
        ]
    )

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 100.0, "temperature": None, "humidity": None, "light": None, "recorded_at": now},
    )

    assert len(service.alert_repo.created) == 1
    assert service.alert_repo.created[0]["metric"] == "moisture"


@pytest.mark.asyncio
async def test_recent_high_moisture_after_watering_does_not_alert():
    now = datetime(2026, 5, 14, 8, 0, tzinfo=timezone.utc)
    service = AlertService.__new__(AlertService)
    service.alert_repo = FakeAlertRepository(existing=None)
    service.plant_repo = FakePlantRepository()
    service.recommendation_service = FakeRecommendationService()
    service.notification_service = FakeNotificationService()
    service.log_repo = FakeLogRepository()
    service.sensor_data_repo = FakeSensorDataRepository(
        [
            SimpleNamespace(moisture=55.0, recorded_at=now - timedelta(hours=3)),
            SimpleNamespace(moisture=100.0, recorded_at=now - timedelta(hours=1)),
            SimpleNamespace(moisture=100.0, recorded_at=now),
        ]
    )

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 100.0, "temperature": None, "humidity": None, "light": None, "recorded_at": now},
    )

    assert service.alert_repo.created == []
    assert service.notification_service.alerts == []
