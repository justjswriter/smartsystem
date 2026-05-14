from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.plant_knowledge import CANONICAL_SPECIES, normalize_species
from app.infrastructure.models import PlantCareProfile


class PlantCareProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_active(self) -> list[PlantCareProfile]:
        result = await self.db.execute(
            select(PlantCareProfile)
            .where(PlantCareProfile.is_active.is_(True))
            .order_by(PlantCareProfile.canonical_species)
        )
        return list(result.scalars().all())

    async def get_by_species(self, species: str | None) -> PlantCareProfile | None:
        normalized = normalize_species(species)
        result = await self.db.execute(
            select(PlantCareProfile).where(
                PlantCareProfile.canonical_species == normalized,
                PlantCareProfile.is_active.is_(True),
            )
        )
        profile = result.scalar_one_or_none()
        if profile:
            return profile

        result = await self.db.execute(
            select(PlantCareProfile).where(
                PlantCareProfile.canonical_species == CANONICAL_SPECIES,
                PlantCareProfile.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()
