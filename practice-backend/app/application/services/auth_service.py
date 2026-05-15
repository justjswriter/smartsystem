from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.auth import LoginRequest, PasswordUpdateRequest, RegisterRequest, UserUpdateRequest
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.enums import UserRole
from app.infrastructure.repositories import SystemLogRepository, UserRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def register(self, payload: RegisterRequest):
        if payload.password != payload.password_confirm:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = await self.user_repo.create(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=UserRole.USER,
        )
        await self.log_repo.create(
            event_type="user_registered",
            message=f"User {user.email} registered",
            user_id=user.id,
        )
        return user

    async def login(self, payload: LoginRequest):
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        token = create_access_token(str(user.id))
        await self.log_repo.create(
            event_type="user_login",
            message=f"User {user.email} logged in",
            user_id=user.id,
        )
        return token, user

    async def update_profile(self, user, payload: UserUpdateRequest):
        values = payload.model_dump(exclude_unset=True)
        if "email" in values and values["email"] != user.email:
            existing = await self.user_repo.get_by_email(values["email"])
            if existing and existing.id != user.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        updated = await self.user_repo.update(user, values=values)
        await self.log_repo.create(
            event_type="user_profile_updated",
            message=f"User {updated.email} updated profile",
            user_id=updated.id,
        )
        return updated

    async def update_password(self, user, payload: PasswordUpdateRequest):
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        if payload.new_password != payload.new_password_confirm:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password",
            )

        await self.user_repo.update(user, values={"password_hash": hash_password(payload.new_password)})
        await self.log_repo.create(
            event_type="user_password_updated",
            message=f"User {user.email} updated password",
            user_id=user.id,
        )
