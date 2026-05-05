from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.sensor import SensorCreate
from app.core.security import generate_device_token, hash_device_token
from app.domain.enums import UserRole
from app.infrastructure.repositories import PlantRepository, SensorRepository, SystemLogRepository
from app.infrastructure.models import User


class SensorService:
    def __init__(self, db: AsyncSession):
        self.sensor_repo = SensorRepository(db)
        self.plant_repo = PlantRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def create(self, *, payload: SensorCreate, current_user: User):
        existing = await self.sensor_repo.get_by_device_id(payload.device_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sensor already exists")
        token = generate_device_token()
        sensor = await self.sensor_repo.create(
            device_id=payload.device_id,
            sensor_type=payload.type,
            user_id=current_user.id,
            token_hash=hash_device_token(token),
        )
        await self.log_repo.create(
            event_type="sensor_registered",
            message=f"Sensor {sensor.device_id} registered",
            user_id=current_user.id,
            payload={"sensor_id": sensor.id},
        )
        return sensor, token

    async def list(self, *, current_user: User, limit: int, offset: int):
        if current_user.role == UserRole.ADMIN:
            return await self.sensor_repo.list(limit=limit, offset=offset)
        return await self.sensor_repo.list_for_user(user_id=current_user.id, limit=limit, offset=offset)

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
        if sensor.user_id and sensor.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sensor does not belong to current user",
            )

        attached = await self.sensor_repo.attach_to_plant(sensor, plant_id)
        await self.log_repo.create(
            event_type="sensor_attached",
            message=f"Sensor {attached.device_id} attached to plant {plant_id}",
            user_id=user_id,
            payload={"sensor_id": attached.id, "plant_id": plant_id},
        )
        return attached

    async def rotate_token(self, *, current_user: User, sensor_id: int):
        sensor = await self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
        if current_user.role != UserRole.ADMIN:
            if sensor.plant_id:
                plant = await self.plant_repo.get_for_user(sensor.plant_id, current_user.id)
                if not plant:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sensor does not belong to your plants")
            elif sensor.user_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sensor does not belong to you")

        token = generate_device_token()
        await self.sensor_repo.update_token_hash(sensor, hash_device_token(token))
        await self.log_repo.create(
            event_type="sensor_token_rotated",
            message=f"Sensor {sensor.device_id} token rotated",
            user_id=current_user.id,
            payload={"sensor_id": sensor.id},
        )
        return sensor, token

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
