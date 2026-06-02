from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.auth import (
    LoginRequest,
    PasswordUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.application.services import AuthService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

USER_UPLOAD_DIR = Path("uploads/users")
MAX_AVATAR_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/register", response_model=UserResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token, user = await service.login(payload)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await AuthService(db).update_profile(current_user, payload)


@router.patch("/me/password", status_code=204)
async def update_password(
    payload: PasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await AuthService(db).update_password(current_user, payload)


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = file.content_type or ""
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP profile photos are supported",
        )

    contents = await file.read()
    if len(contents) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Profile photo must be 5 MB or smaller",
        )

    USER_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"user-{current_user.id}-{uuid4().hex}{extension}"
    file_path = USER_UPLOAD_DIR / filename
    file_path.write_bytes(contents)

    return await AuthService(db).update_profile(
        current_user,
        UserUpdateRequest(avatar_url=f"/uploads/users/{filename}"),
    )
