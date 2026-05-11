from types import SimpleNamespace

import pytest

from app.application.schemas.plant import PlantCreate, PlantUpdate
from app.application.services.plant_service import PlantService
from app.domain.plant_knowledge import CANONICAL_SPECIES, resolve_plant_profile


def test_unknown_species_resolves_to_default_profile():
    profile = resolve_plant_profile("Mint")

    assert profile.slug == "epipremnum_aureum"
    assert profile.canonical_species == CANONICAL_SPECIES
    assert profile.thresholds["moisture"].min == 35.0


class FakePlantRepository:
    def __init__(self):
        self.created_payload = None
        self.updated_payload = None
        self.plant = SimpleNamespace(id=7, user_id=42, species="Mint")

    async def create(self, *, user_id: int, payload: dict):
        self.created_payload = payload
        return SimpleNamespace(id=1, user_id=user_id, **payload)

    async def get_for_user(self, plant_id: int, user_id: int):
        return self.plant

    async def update(self, plant, payload: dict):
        self.updated_payload = payload
        for key, value in payload.items():
            setattr(plant, key, value)
        return plant


class FakeLogRepository:
    async def create(self, **kwargs):
        return SimpleNamespace(**kwargs)


@pytest.mark.asyncio
async def test_plant_create_normalizes_species_to_supported_type():
    service = PlantService.__new__(PlantService)
    service.plant_repo = FakePlantRepository()
    service.log_repo = FakeLogRepository()

    plant = await service.create(
        user_id=42,
        payload=PlantCreate(name="Kitchen plant", species="Mint", location="Kitchen"),
    )

    assert plant.species == CANONICAL_SPECIES
    assert service.plant_repo.created_payload["species"] == CANONICAL_SPECIES


@pytest.mark.asyncio
async def test_plant_update_normalizes_species_to_supported_type():
    service = PlantService.__new__(PlantService)
    service.plant_repo = FakePlantRepository()

    plant = await service.update(user_id=42, plant_id=7, payload=PlantUpdate(species="Basil"))

    assert plant.species == CANONICAL_SPECIES
    assert service.plant_repo.updated_payload["species"] == CANONICAL_SPECIES
