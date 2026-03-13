from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate
from app.utils.security import hash_password


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create(session: AsyncSession, user_data: UserCreate) -> User:
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
