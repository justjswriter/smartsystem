from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SensorData

MAX_HISTORY_POINTS = 500


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

    async def history_for_plant(self, plant_id: int, hours: int, max_points: int = MAX_HISTORY_POINTS) -> list[SensorData]:
        from_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
        count_result = await self.db.execute(
            select(func.count())
            .select_from(SensorData)
            .where(SensorData.plant_id == plant_id, SensorData.recorded_at >= from_dt)
        )
        total_points = int(count_result.scalar_one())
        if total_points <= max_points:
            result = await self.db.execute(
                select(SensorData)
                .where(SensorData.plant_id == plant_id, SensorData.recorded_at >= from_dt)
                .order_by(SensorData.recorded_at.asc())
            )
            return list(result.scalars().all())

        bucket_seconds = max(1, (hours * 3600 + max_points - 1) // max_points)
        epoch_bucket = func.floor(func.extract("epoch", SensorData.recorded_at) / bucket_seconds) * bucket_seconds
        recorded_bucket = func.to_timestamp(epoch_bucket)
        result = await self.db.execute(
            select(
                recorded_bucket.label("recorded_at"),
                func.avg(SensorData.moisture).label("moisture"),
                func.avg(SensorData.temperature).label("temperature"),
                func.avg(SensorData.humidity).label("humidity"),
                func.avg(SensorData.light).label("light"),
            )
            .where(SensorData.plant_id == plant_id, SensorData.recorded_at >= from_dt)
            .group_by(recorded_bucket)
            .order_by(recorded_bucket.asc())
        )
        return [
            SimpleNamespace(
                recorded_at=row.recorded_at,
                moisture=float(row.moisture) if row.moisture is not None else None,
                temperature=float(row.temperature) if row.temperature is not None else None,
                humidity=float(row.humidity) if row.humidity is not None else None,
                light=float(row.light) if row.light is not None else None,
            )
            for row in result
        ]
