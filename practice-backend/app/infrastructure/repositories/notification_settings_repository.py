from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import UserNotificationSettings


class NotificationSettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> UserNotificationSettings | None:
        result = await self.db.execute(
            select(UserNotificationSettings).where(UserNotificationSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_user(self, user_id: int) -> UserNotificationSettings:
        settings = await self.get_by_user_id(user_id)
        if settings:
            return settings

        settings = UserNotificationSettings(user_id=user_id)
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update_for_user(self, *, user_id: int, values: dict) -> UserNotificationSettings:
        settings = await self.get_or_create_for_user(user_id)
        for key, value in values.items():
            setattr(settings, key, value)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings
