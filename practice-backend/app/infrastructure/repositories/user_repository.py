from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, full_name: str, email: str, password_hash: str, role) -> User:
        user = User(full_name=full_name, email=email, password_hash=password_hash, role=role)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, *, values: dict) -> User:
        for key, value in values.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list(self, *, limit: int, offset: int) -> list[User]:
        result = await self.db.execute(select(User).offset(offset).limit(limit))
        return list(result.scalars().all())
