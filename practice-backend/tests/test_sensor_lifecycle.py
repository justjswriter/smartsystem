from datetime import datetime, timezone
from types import MethodType, SimpleNamespace

import httpx
import pytest

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import hash_device_token
from app.domain.enums import SensorStatus, SensorType, UserRole
from app.main import app
from app.application.schemas.sensor import SensorCreate
from app.application.services.alert_service import AlertService
from app.application.services.sensor_service import SensorService


def user(user_id: int, role: UserRole = UserRole.USER):
    return SimpleNamespace(id=user_id, role=role, is_active=True, full_name=f"User {user_id}")


def sensor(sensor_id: int, *, user_id=None, plant_id=None, token_hash=None):
    return SimpleNamespace(
        id=sensor_id,
        user_id=user_id,
        device_id=f"sensor-{sensor_id}",
        type=SensorType.MULTI,
        status=SensorStatus.OFFLINE,
        plant_id=plant_id,
        is_active=True,
        device_token_hash=token_hash,
        last_seen_at=None,
        last_ingest_source=None,
        last_error_at=None,
        last_error_message=None,
    )


class FakeSensorRepo:
    def __init__(self, sensors=None):
        self.sensors = {item.id: item for item in sensors or []}
        self.created = []

    async def get_by_device_id(self, device_id):
        return next((item for item in self.sensors.values() if item.device_id == device_id), None)

    async def get_by_id(self, sensor_id):
        return self.sensors.get(sensor_id)

    async def create(self, *, device_id, sensor_type, user_id, token_hash):
        item = sensor(len(self.sensors) + 1, user_id=user_id, token_hash=token_hash)
        item.device_id = device_id
        item.type = sensor_type
        self.sensors[item.id] = item
        self.created.append(item)
        return item

    async def assign_to_user(self, item, user_id):
        item.user_id = user_id
        return item

    async def attach_to_plant(self, item, plant_id):
        item.plant_id = plant_id
        item.status = SensorStatus.ONLINE
        item.last_seen_at = datetime.now(timezone.utc)
        return item

    async def detach_from_plant(self, item):
        item.plant_id = None
        item.status = SensorStatus.OFFLINE
        return item

    async def update_token_hash(self, item, token_hash):
        item.device_token_hash = token_hash
        return item

    async def touch_seen(self, item, source=None):
        item.status = SensorStatus.ONLINE
        item.last_seen_at = datetime.now(timezone.utc)
        item.last_ingest_source = source

    async def mark_error(self, item, message, source=None):
        item.last_error_message = message
        item.last_ingest_source = source

    async def list_for_user(self, *, user_id, limit, offset):
        owned = [
            item
            for item in self.sensors.values()
            if item.user_id == user_id or getattr(getattr(item, "plant", None), "user_id", None) == user_id
        ]
        return owned[offset : offset + limit]


class FakePlantRepo:
    def __init__(self, plants):
        self.plants = {item.id: item for item in plants}

    async def get_by_id(self, plant_id):
        return self.plants.get(plant_id)


class FakeUserRepo:
    def __init__(self, users):
        self.users = {item.id: item for item in users}

    async def get_by_id(self, user_id):
        return self.users.get(user_id)


class FakeLogRepo:
    async def create(self, **kwargs):
        return SimpleNamespace(**kwargs)


class FakeSensorDataRepo:
    async def create(self, *, sensor_id, plant_id, payload):
        return SimpleNamespace(id=77, sensor_id=sensor_id, plant_id=plant_id, **payload)


def make_sensor_service(*, sensors=None, plants=None, users=None):
    service = SensorService.__new__(SensorService)
    service.sensor_repo = FakeSensorRepo(sensors)
    service.plant_repo = FakePlantRepo(plants or [])
    service.user_repo = FakeUserRepo(users or [])
    service.log_repo = FakeLogRepo()
    return service


@pytest.mark.asyncio
async def test_user_cannot_mutate_sensor_endpoints():
    async def override_current_user():
        return user(10, UserRole.USER)

    async def override_db():
        yield SimpleNamespace()

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db] = override_db
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            responses = [
                await client.post("/api/v1/sensors", json={"device_id": "sensor-403", "type": "multi"}),
                await client.post("/api/v1/sensors/1/attach", json={"plant_id": 1}),
                await client.post("/api/v1/sensors/1/detach"),
                await client.post("/api/v1/sensors/1/rotate-token"),
                await client.post("/api/v1/sensors/1/assign", json={"user_id": 10}),
            ]
        assert [response.status_code for response in responses] == [403, 403, 403, 403, 403]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_can_create_sensor_and_receives_token():
    service = make_sensor_service()
    created, token = await service.create(
        payload=SensorCreate(device_id="arduino-uno-999", type=SensorType.MULTI),
        current_user=user(1, UserRole.ADMIN),
    )

    assert created.device_id == "arduino-uno-999"
    assert created.user_id is None
    assert token
    assert created.device_token_hash != token


@pytest.mark.asyncio
async def test_admin_can_assign_sensor_to_user():
    item = sensor(1)
    service = make_sensor_service(sensors=[item], users=[user(22)])

    assigned = await service.assign(admin_user=user(1, UserRole.ADMIN), sensor_id=1, user_id=22)

    assert assigned.user_id == 22


@pytest.mark.asyncio
async def test_assign_validates_attached_plant_owner_consistency():
    item = sensor(1, plant_id=100)
    service = make_sensor_service(
        sensors=[item],
        plants=[SimpleNamespace(id=100, user_id=10)],
        users=[user(20)],
    )

    with pytest.raises(Exception) as exc:
        await service.assign(admin_user=user(1, UserRole.ADMIN), sensor_id=1, user_id=20)

    assert "different user" in str(exc.value)


@pytest.mark.asyncio
async def test_attach_validates_sensor_user_and_plant_owner_consistency():
    assigned_to_other = sensor(1, user_id=20)
    service = make_sensor_service(
        sensors=[assigned_to_other],
        plants=[SimpleNamespace(id=100, user_id=10)],
    )

    with pytest.raises(Exception) as exc:
        await service.attach(admin_user=user(1, UserRole.ADMIN), sensor_id=1, plant_id=100)

    assert "different user" in str(exc.value)


@pytest.mark.asyncio
async def test_attach_auto_assigns_unassigned_sensor_to_plant_owner():
    item = sensor(1)
    service = make_sensor_service(sensors=[item], plants=[SimpleNamespace(id=100, user_id=10)])

    attached = await service.attach(admin_user=user(1, UserRole.ADMIN), sensor_id=1, plant_id=100)

    assert attached.user_id == 10
    assert attached.plant_id == 100


@pytest.mark.asyncio
async def test_user_list_returns_only_assigned_or_attached_sensors():
    own = sensor(1, user_id=10)
    attached = sensor(2)
    attached.plant = SimpleNamespace(user_id=10)
    other = sensor(3, user_id=20)
    repo = FakeSensorRepo([own, attached, other])

    visible = await repo.list_for_user(user_id=10, limit=20, offset=0)

    assert [item.id for item in visible] == [1, 2]


@pytest.mark.asyncio
async def test_gateway_ingest_still_works_with_same_token_and_payload(monkeypatch):
    token = "plain-device-token"
    item = sensor(1, user_id=10, plant_id=100, token_hash=hash_device_token(token))
    service = AlertService.__new__(AlertService)
    service.sensor_repo = FakeSensorRepo([item])
    service.sensor_data_repo = FakeSensorDataRepo()
    service.log_repo = FakeLogRepo()

    async def no_thresholds(self, *, sensor_id, plant_id, payload):
        return None

    async def no_publish(*args, **kwargs):
        return None

    service._evaluate_thresholds = MethodType(no_thresholds, service)
    monkeypatch.setattr("app.application.services.alert_service.event_bus.publish", no_publish)

    data = await service.ingest_sensor_data(
        device_id="sensor-1",
        device_token=token,
        source="test-gateway",
        payload={"moisture": 45.0, "temperature": 22.0, "humidity": 55.0, "light": 600.0},
    )

    assert data.id == 77
    assert item.status == SensorStatus.ONLINE
    assert item.last_ingest_source == "test-gateway"
