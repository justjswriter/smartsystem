from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user_repository import create, get_by_email
from app.schemas.auth import Token, UserCreate, UserLogin
from app.utils.security import create_access_token, verify_password


async def register(db: AsyncSession, user_data: UserCreate):
    if await get_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await create(db, user_data)
    return user


async def login(db: AsyncSession, credentials: UserLogin) -> Token:
    user = await get_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is inactive",
        )
    return Token(access_token=create_access_token(user.id))

