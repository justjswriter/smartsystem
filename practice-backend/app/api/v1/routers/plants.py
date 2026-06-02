from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.plant import PlantCreate, PlantResponse, PlantUpdate
from app.application.services import PlantService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/plants", tags=["plants"])

PLANT_UPLOAD_DIR = Path("uploads/plants")
MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


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


@router.post("/{plant_id}/photo", response_model=PlantResponse)
async def upload_plant_photo(
    plant_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = file.content_type or ""
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP plant photos are supported",
        )

    contents = await file.read()
    if len(contents) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Plant photo must be 5 MB or smaller",
        )

    service = PlantService(db)
    await service.get(user_id=current_user.id, plant_id=plant_id)

    PLANT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"plant-{plant_id}-{uuid4().hex}{extension}"
    file_path = PLANT_UPLOAD_DIR / filename
    file_path.write_bytes(contents)

    return await service.update(
        user_id=current_user.id,
        plant_id=plant_id,
        payload=PlantUpdate(image_url=f"/uploads/plants/{filename}"),
    )


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await PlantService(db).delete(user_id=current_user.id, plant_id=plant_id)
