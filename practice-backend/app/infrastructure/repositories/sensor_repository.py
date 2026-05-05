from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import SensorStatus
from app.infrastructure.models import Sensor


class SensorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, device_id: str, sensor_type, user_id: int | None, token_hash: str) -> Sensor:
        sensor = Sensor(device_id=device_id, type=sensor_type, user_id=user_id, device_token_hash=token_hash)
        self.db.add(sensor)
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def get_by_device_id(self, device_id: str) -> Sensor | None:
        result = await self.db.execute(select(Sensor).where(Sensor.device_id == device_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, sensor_id: int) -> Sensor | None:
        result = await self.db.execute(select(Sensor).where(Sensor.id == sensor_id))
        return result.scalar_one_or_none()

    async def list(self, *, limit: int, offset: int) -> list[Sensor]:
        result = await self.db.execute(select(Sensor).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def list_for_user(self, *, user_id: int, limit: int, offset: int) -> list[Sensor]:
        result = await self.db.execute(
            select(Sensor)
            .outerjoin(Sensor.plant)
            .where(or_(Sensor.user_id == user_id, Sensor.plant.has(user_id=user_id)))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def attach_to_plant(self, sensor: Sensor, plant_id: int) -> Sensor:
        sensor.plant_id = plant_id
        sensor.status = SensorStatus.ONLINE
        sensor.last_seen_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def detach_from_plant(self, sensor: Sensor) -> Sensor:
        sensor.plant_id = None
        sensor.status = SensorStatus.OFFLINE
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def touch_seen(self, sensor: Sensor, source: str | None = None) -> None:
        sensor.last_seen_at = datetime.now(timezone.utc)
        sensor.status = SensorStatus.ONLINE
        sensor.last_ingest_source = source
        sensor.last_error_at = None
        sensor.last_error_message = None
        await self.db.commit()

    async def update_token_hash(self, sensor: Sensor, token_hash: str) -> Sensor:
        sensor.device_token_hash = token_hash
        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def mark_error(self, sensor: Sensor, message: str, source: str | None = None) -> None:
        sensor.last_error_at = datetime.now(timezone.utc)
        sensor.last_error_message = message
        sensor.last_ingest_source = source
        await self.db.commit()
