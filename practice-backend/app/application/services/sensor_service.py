from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.sensor import SensorCreate
from app.infrastructure.repositories import PlantRepository, SensorRepository, SystemLogRepository


class SensorService:
    def __init__(self, db: AsyncSession):
        self.sensor_repo = SensorRepository(db)
        self.plant_repo = PlantRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def create(self, payload: SensorCreate):
        existing = await self.sensor_repo.get_by_device_id(payload.device_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sensor already exists")
        return await self.sensor_repo.create(device_id=payload.device_id, sensor_type=payload.type)

    async def list(self, *, limit: int, offset: int):
        return await self.sensor_repo.list(limit=limit, offset=offset)

    async def attach(self, *, user_id: int, sensor_id: int, plant_id: int):
        sensor = await self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")

        plant = await self.plant_repo.get_for_user(plant_id, user_id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plant not found or not owned by current user",
            )

        if sensor.plant_id and sensor.plant_id != plant_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Sensor is already attached to another plant",
            )

        attached = await self.sensor_repo.attach_to_plant(sensor, plant_id)
        await self.log_repo.create(
            event_type="sensor_attached",
            message=f"Sensor {attached.device_id} attached to plant {plant_id}",
            user_id=user_id,
            payload={"sensor_id": attached.id, "plant_id": plant_id},
        )
        return attached

    async def detach(self, *, user_id: int, sensor_id: int):
        sensor = await self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
        if not sensor.plant_id:
            return sensor

        plant = await self.plant_repo.get_for_user(sensor.plant_id, user_id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sensor does not belong to your plants",
            )

        detached = await self.sensor_repo.detach_from_plant(sensor)
        await self.log_repo.create(
            event_type="sensor_detached",
            message=f"Sensor {detached.device_id} detached",
            user_id=user_id,
            payload={"sensor_id": detached.id},
        )
        return detached
