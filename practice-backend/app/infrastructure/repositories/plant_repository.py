from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import Plant


class PlantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, user_id: int, payload: dict) -> Plant:
        plant = Plant(user_id=user_id, **payload)
        self.db.add(plant)
        await self.db.commit()
        await self.db.refresh(plant)
        return plant

    async def list_for_user(self, user_id: int) -> list[Plant]:
        result = await self.db.execute(
            select(Plant).where(Plant.user_id == user_id, Plant.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def get_by_id(self, plant_id: int) -> Plant | None:
        result = await self.db.execute(select(Plant).where(Plant.id == plant_id, Plant.is_active.is_(True)))
        return result.scalar_one_or_none()

    async def get_for_user(self, plant_id: int, user_id: int) -> Plant | None:
        result = await self.db.execute(
            select(Plant).where(
                Plant.id == plant_id, Plant.user_id == user_id, Plant.is_active.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, plant: Plant, payload: dict) -> Plant:
        for key, value in payload.items():
            setattr(plant, key, value)
        await self.db.commit()
        await self.db.refresh(plant)
        return plant

    async def soft_delete(self, plant: Plant) -> Plant:
        plant.is_active = False
        plant.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(plant)
        return plant
