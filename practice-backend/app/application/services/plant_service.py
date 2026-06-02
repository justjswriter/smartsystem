from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.plant import PlantCreate, PlantUpdate
from app.domain.plant_knowledge import normalize_species
from app.infrastructure.repositories import PlantRepository, SensorRepository, SystemLogRepository


class PlantService:
    def __init__(self, db: AsyncSession):
        self.plant_repo = PlantRepository(db)
        self.sensor_repo = SensorRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def create(self, *, user_id: int, payload: PlantCreate):
        plant_payload = payload.model_dump()
        plant_payload["species"] = normalize_species(plant_payload.get("species"))
        plant = await self.plant_repo.create(user_id=user_id, payload=plant_payload)
        await self.log_repo.create(
            event_type="plant_created",
            message=f"Plant {plant.id} created",
            user_id=user_id,
            payload={"plant_id": plant.id},
        )
        return plant

    async def list(self, *, user_id: int):
        return await self.plant_repo.list_for_user(user_id)

    async def get(self, *, user_id: int, plant_id: int):
        plant = await self.plant_repo.get_for_user(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
        return plant

    async def update(self, *, user_id: int, plant_id: int, payload: PlantUpdate):
        plant = await self.get(user_id=user_id, plant_id=plant_id)
        updated_payload = payload.model_dump(exclude_none=True)
        if "species" in updated_payload:
            updated_payload["species"] = normalize_species(updated_payload.get("species"))
        if not updated_payload:
            return plant
        return await self.plant_repo.update(plant, updated_payload)

    async def delete(self, *, user_id: int, plant_id: int):
        plant = await self.get(user_id=user_id, plant_id=plant_id)
        await self.plant_repo.soft_delete(plant)
        await self.log_repo.create(
            event_type="plant_deleted",
            message=f"Plant {plant.id} deactivated",
            user_id=user_id,
            payload={"plant_id": plant.id},
        )
        return {"status": "deleted", "plant_id": plant.id}
