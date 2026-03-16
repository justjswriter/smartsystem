from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.plant import PlantCreate, PlantResponse, PlantUpdate
from app.application.services import PlantService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("", response_model=PlantResponse)
async def create_plant(
    payload: PlantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PlantService(db).create(user_id=current_user.id, payload=payload)


@router.get("", response_model=list[PlantResponse])
async def list_plants(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await PlantService(db).list(user_id=current_user.id)


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await PlantService(db).get(user_id=current_user.id, plant_id=plant_id)


@router.patch("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    payload: PlantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PlantService(db).update(user_id=current_user.id, plant_id=plant_id, payload=payload)


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await PlantService(db).delete(user_id=current_user.id, plant_id=plant_id)
