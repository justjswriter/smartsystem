from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.plant_care_profile import PlantCareProfileResponse
from app.application.services import PlantCareProfileService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/plant-care-profiles", tags=["plant-care-profiles"])


@router.get("", response_model=list[PlantCareProfileResponse])
async def list_plant_care_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return await PlantCareProfileService(db).list_profiles()


@router.get("/resolve", response_model=PlantCareProfileResponse | None)
async def resolve_plant_care_profile(
    species: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return await PlantCareProfileService(db).get_by_species(species)
