from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading


class ReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reading_id: int) -> Optional[SensorReading]:
        return self.db.get(SensorReading, reading_id)

    def create(
        self,
        *,
        plant_id: int,
        sensor_id: Optional[int],
        device_id: str,
        soil_moisture_raw: Optional[int],
        soil_moisture_percent: Optional[float],
        temperature: Optional[float],
        humidity: Optional[float],
        light_raw: Optional[int],
        light_percent: Optional[float],
        recorded_at: Optional[datetime] = None,
        commit: bool = True,
    ) -> SensorReading:
        r = SensorReading(
            plant_id=plant_id,
            sensor_id=sensor_id,
            device_id=device_id,
            soil_moisture_raw=soil_moisture_raw,
            soil_moisture_percent=soil_moisture_percent,
            temperature=temperature,
            humidity=humidity,
            light_raw=light_raw,
            light_percent=light_percent,
        )
        if recorded_at is not None:
            r.recorded_at = recorded_at
        self.db.add(r)
        if commit:
            self.db.commit()
            self.db.refresh(r)
        else:
            self.db.flush()
            self.db.refresh(r)
        return r

    def list_by_plant(
        self, plant_id: int, limit: int = 200, offset: int = 0
    ) -> List[SensorReading]:
        q = (
            select(SensorReading)
            .where(SensorReading.plant_id == plant_id)
            .order_by(desc(SensorReading.recorded_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(q).scalars().all())

    def latest_for_plant(self, plant_id: int) -> Optional[SensorReading]:
        q = (
            select(SensorReading)
            .where(SensorReading.plant_id == plant_id)
            .order_by(desc(SensorReading.recorded_at))
            .limit(1)
        )
        return self.db.execute(q).scalar_one_or_none()

    def count_for_plant(self, plant_id: int) -> int:
        from sqlalchemy import func
        c = self.db.execute(
            select(func.count()).select_from(SensorReading).where(
                SensorReading.plant_id == plant_id
            )
        ).scalar()
        return int(c or 0)
