from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.application.services.alert_service import AlertService
from app.application.services.notification_service import NotificationService
from app.domain.enums import AlertSeverity, NotificationSeverity, NotificationType


class FakeAlertRepository:
    def __init__(self, *, existing=None, severity=AlertSeverity.MEDIUM):
        self.existing = existing
        self.severity = severity
        self.created = []

    async def find_open_by_metric(self, *, plant_id: int, metric: str):
        return self.existing

    async def create(self, payload: dict):
        self.created.append(payload)
        return SimpleNamespace(id=123, **payload)

    async def add_transition(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakePlantRepository:
    async def get_by_id(self, plant_id: int):
        return SimpleNamespace(id=plant_id, user_id=42, species="Golden pothos")


class FakeRecommendationService:
    async def create_for_alert(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeNotificationService:
    def __init__(self):
        self.alerts = []

    async def create_for_alert(self, *, alert, issue_code=None):
        self.alerts.append((alert, issue_code))
        return SimpleNamespace(id=1), True


class FakeLogRepository:
    async def create(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeNotificationRepository:
    def __init__(self, notifications=None):
        self.notifications = list(notifications or [])
        self.created = []

    async def find_unread_by_dedupe_key(self, *, user_id, dedupe_key):
        return next(
            (
                item
                for item in self.notifications
                if item.user_id == user_id and item.dedupe_key == dedupe_key and item.read_at is None
            ),
            None,
        )

    async def create(self, payload):
        item = SimpleNamespace(id=len(self.notifications) + 1, read_at=None, created_at=datetime.now(timezone.utc), **payload)
        self.notifications.append(item)
        self.created.append(item)
        return item

    async def list_for_user(self, *, user_id, unread_only, limit, offset):
        items = [item for item in self.notifications if item.user_id == user_id]
        if unread_only:
            items = [item for item in items if item.read_at is None]
        return items[offset : offset + limit]

    async def get_for_user(self, *, user_id, notification_id):
        return next(
            (item for item in self.notifications if item.user_id == user_id and item.id == notification_id),
            None,
        )

    async def mark_read(self, notification):
        notification.read_at = datetime.now(timezone.utc)
        return notification

    async def mark_all_read(self, *, user_id):
        items = [item for item in self.notifications if item.user_id == user_id and item.read_at is None]
        now = datetime.now(timezone.utc)
        for item in items:
            item.read_at = now
        return items


def make_alert_service(*, existing=None):
    service = AlertService.__new__(AlertService)
    service.alert_repo = FakeAlertRepository(existing=existing)
    service.plant_repo = FakePlantRepository()
    service.recommendation_service = FakeRecommendationService()
    service.notification_service = FakeNotificationService()
    service.log_repo = FakeLogRepository()
    return service


def make_notification_service(notifications=None):
    service = NotificationService.__new__(NotificationService)
    service.notification_repo = FakeNotificationRepository(notifications)
    return service


def notification(notification_id, *, user_id, read_at=None, dedupe_key=None):
    return SimpleNamespace(
        id=notification_id,
        user_id=user_id,
        type=NotificationType.PLANT_CONDITION,
        severity=NotificationSeverity.WARNING,
        title_key="notification.alert.condition.title",
        message_key="notification.alert.condition.message",
        params={},
        title=None,
        message=None,
        related_plant_id=1,
        related_alert_id=1,
        related_sensor_id=None,
        dedupe_key=dedupe_key,
        read_at=read_at,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_alert_creation_creates_notification(monkeypatch):
    async def no_publish(*args, **kwargs):
        return None

    monkeypatch.setattr("app.application.services.alert_service.event_bus.publish", no_publish)
    service = make_alert_service()

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 10.0, "temperature": None, "humidity": None, "light": None},
    )

    assert len(service.notification_service.alerts) == 1
    alert, issue_code = service.notification_service.alerts[0]
    assert alert.user_id == 42
    assert alert.plant_id == 3
    assert issue_code == "low_moisture"


@pytest.mark.asyncio
async def test_duplicate_readings_with_open_alert_do_not_spam_notifications():
    service = make_alert_service(existing=SimpleNamespace(id=99))

    await service._evaluate_thresholds(
        sensor_id=7,
        plant_id=3,
        payload={"moisture": 10.0, "temperature": None, "humidity": None, "light": None},
    )

    assert service.alert_repo.created == []
    assert service.notification_service.alerts == []


@pytest.mark.asyncio
async def test_critical_alert_creates_critical_notification(monkeypatch):
    async def no_publish(*args, **kwargs):
        return None

    monkeypatch.setattr("app.application.services.notification_service.event_bus.publish", no_publish)
    service = make_notification_service()
    alert = SimpleNamespace(
        id=5,
        user_id=10,
        plant_id=3,
        sensor_id=2,
        metric="moisture",
        severity=AlertSeverity.CRITICAL,
        title="Moisture threshold below",
        message="Moisture is below threshold",
    )

    created, was_created = await service.create_for_alert(alert=alert, issue_code="low_soil_moisture")

    assert was_created is True
    assert created.type == NotificationType.CRITICAL_ALERT
    assert created.severity == NotificationSeverity.CRITICAL
    assert created.dedupe_key == "alert:3:moisture"


@pytest.mark.asyncio
async def test_notification_dedupe_skips_existing_unread(monkeypatch):
    async def no_publish(*args, **kwargs):
        return None

    monkeypatch.setattr("app.application.services.notification_service.event_bus.publish", no_publish)
    existing = notification(1, user_id=10, dedupe_key="alert:3:moisture")
    service = make_notification_service([existing])

    created, was_created = await service.create_once(
        payload={
            "user_id": 10,
            "type": NotificationType.PLANT_CONDITION,
            "severity": NotificationSeverity.WARNING,
            "title_key": "notification.alert.condition.title",
            "message_key": "notification.alert.condition.message",
            "dedupe_key": "alert:3:moisture",
        }
    )

    assert created is existing
    assert was_created is False
    assert service.notification_repo.created == []


@pytest.mark.asyncio
async def test_user_lists_only_own_notifications():
    service = make_notification_service(
        [notification(1, user_id=10), notification(2, user_id=20), notification(3, user_id=10)]
    )

    visible = await service.list_for_user(user_id=10, unread_only=False, limit=20, offset=0)

    assert [item.id for item in visible] == [1, 3]


@pytest.mark.asyncio
async def test_user_cannot_mark_another_users_notification_read():
    service = make_notification_service([notification(1, user_id=20)])

    with pytest.raises(Exception) as exc:
        await service.mark_read(user_id=10, notification_id=1)

    assert "Notification not found" in str(exc.value)


@pytest.mark.asyncio
async def test_mark_read_and_mark_all_set_read_at(monkeypatch):
    async def no_publish(*args, **kwargs):
        return None

    monkeypatch.setattr("app.application.services.notification_service.event_bus.publish", no_publish)
    first = notification(1, user_id=10)
    second = notification(2, user_id=10)
    other = notification(3, user_id=20)
    service = make_notification_service([first, second, other])

    marked = await service.mark_read(user_id=10, notification_id=1)
    assert marked.read_at is not None

    await service.mark_all_read(user_id=10)
    assert first.read_at is not None
    assert second.read_at is not None
    assert other.read_at is None
