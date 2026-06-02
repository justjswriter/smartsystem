from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plant import Plant
from app.models.sensor import Sensor, SensorStatus, SensorType


class SensorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sensor_id: int) -> Optional[Sensor]:
        return self.db.get(Sensor, sensor_id)

    def get_by_device_id(self, device_id: str) -> Optional[Sensor]:
        return self.db.execute(
            select(Sensor).where(Sensor.device_id == device_id)
        ).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
    ) -> List[Sensor]:
        """Sensors that belong to one of the user's active plants (assigned only)."""
        q = (
            select(Sensor)
            .join(Plant, Plant.id == Sensor.plant_id)
            .where(Plant.user_id == user_id, Plant.is_active.is_(True))
        )
        return list(self.db.execute(q).scalars().all())

    def list_for_plant(
        self,
        plant_id: int,
    ) -> List[Sensor]:
        return list(
            self.db.execute(
                select(Sensor).where(Sensor.plant_id == plant_id)
            ).scalars().all()
        )

    def create(
        self,
        device_id: str,
        plant_id: Optional[int],
        sensor_type: SensorType = SensorType.multi,
        status: SensorStatus = SensorStatus.offline,
        commit: bool = True,
    ) -> Sensor:
        s = Sensor(
            device_id=device_id,
            plant_id=plant_id,
            sensor_type=sensor_type,
            status=status,
        )
        self.db.add(s)
        if commit:
            self.db.commit()
            self.db.refresh(s)
        else:
            self.db.flush()
            self.db.refresh(s)
        return s

    def save(self, sensor: Sensor, commit: bool = True) -> Sensor:
        self.db.add(sensor)
        if commit:
            self.db.commit()
            self.db.refresh(sensor)
        else:
            self.db.flush()
            self.db.refresh(sensor)
        return sensor
