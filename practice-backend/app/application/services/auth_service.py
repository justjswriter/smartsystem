from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.auth import LoginRequest, RegisterRequest
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
