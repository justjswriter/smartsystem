from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.plant import Plant
from app.models.user import User
from app.repositories.plant_repository import PlantRepository
from app.schemas.plant import PlantCreate, PlantOut, PlantUpdate


def _ensure_plant(plant: Plant | None) -> Plant:
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def create_plant(db: Session, user: User, data: PlantCreate) -> PlantOut:
    repo = PlantRepository(db)
    p = repo.create(
        user_id=user.id,
        name=data.name,
        species=data.species,
        location=data.location,
        description=data.description,
    )
    return PlantOut.model_validate(p)


def list_plants(db: Session, user: User) -> List[PlantOut]:
    repo = PlantRepository(db)
    plants = repo.list_for_user(user.id, only_active=True)
    return [PlantOut.model_validate(p) for p in plants]


def get_plant(db: Session, user: User, plant_id: int) -> PlantOut:
    repo = PlantRepository(db)
    p = _ensure_plant(repo.get_by_id_for_user(plant_id, user.id, include_inactive=True))
    if not p.is_active:
        raise HTTPException(status_code=404, detail="Plant not found")
    return PlantOut.model_validate(p)


def update_plant(
    db: Session, user: User, plant_id: int, data: PlantUpdate
) -> PlantOut:
    repo = PlantRepository(db)
    p = _ensure_plant(repo.get_by_id_for_user(plant_id, user.id, include_inactive=True))
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    repo.save(p)
    return PlantOut.model_validate(p)


def soft_delete_plant(db: Session, user: User, plant_id: int) -> None:
    repo = PlantRepository(db)
    p = _ensure_plant(repo.get_by_id_for_user(plant_id, user.id, include_inactive=True))
    repo.soft_delete(p)


def get_plant_entity_for_user(
    db: Session, user: User, plant_id: int, allow_inactive: bool = False
) -> Plant:
    """Used by other services to enforce ownership."""
    repo = PlantRepository(db)
    p = repo.get_by_id_for_user(
        plant_id, user.id, include_inactive=allow_inactive
    )
    if not p or (not allow_inactive and not p.is_active):
        raise HTTPException(status_code=404, detail="Plant not found")
    return p
