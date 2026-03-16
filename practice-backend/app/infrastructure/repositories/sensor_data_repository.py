from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SensorData


class SensorDataRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, sensor_id: int, plant_id: int, payload: dict) -> SensorData:
        recorded_at = payload.get("recorded_at") or datetime.now(timezone.utc)
        data = SensorData(
            sensor_id=sensor_id,
            plant_id=plant_id,
            moisture=payload.get("moisture"),
            temperature=payload.get("temperature"),
            humidity=payload.get("humidity"),
            light=payload.get("light"),
            recorded_at=recorded_at,
        )
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

    async def latest_for_plant(self, plant_id: int) -> SensorData | None:
        result = await self.db.execute(
            select(SensorData)
            .where(SensorData.plant_id == plant_id)
            .order_by(desc(SensorData.recorded_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def history_for_plant(self, plant_id: int, hours: int) -> list[SensorData]:
        from_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self.db.execute(
            select(SensorData)
            .where(SensorData.plant_id == plant_id, SensorData.recorded_at >= from_dt)
            .order_by(SensorData.recorded_at.asc())
        )
        return list(result.scalars().all())
