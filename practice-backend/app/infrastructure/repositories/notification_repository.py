from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> Notification:
        notification = Notification(**payload)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def find_unread_by_dedupe_key(self, *, user_id: int, dedupe_key: str) -> Notification | None:
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.dedupe_key == dedupe_key,
                Notification.read_at.is_(None),
            )
            .order_by(Notification.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: int,
        unread_only: bool,
        limit: int,
        offset: int,
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.read_at.is_(None))
        result = await self.db.execute(
            stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_for_user(self, *, user_id: int, notification_id: int) -> Notification | None:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def mark_read(self, notification: Notification) -> Notification:
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, *, user_id: int) -> list[Notification]:
        notifications = await self.list_for_user(user_id=user_id, unread_only=True, limit=1000, offset=0)
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.read_at = now
        await self.db.commit()
        for notification in notifications:
            await self.db.refresh(notification)
        return notifications
