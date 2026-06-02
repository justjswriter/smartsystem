from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SystemLog


class SystemLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, *, event_type: str, message: str, user_id: int | None = None, payload: dict | None = None
    ) -> SystemLog:
        item = SystemLog(
            event_type=event_type,
            message=message,
            user_id=user_id,
            payload=payload,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        event_type: str | None = None,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[SystemLog]:
        stmt = select(SystemLog)
        if event_type:
            stmt = stmt.where(SystemLog.event_type == event_type)
        if user_id:
            stmt = stmt.where(SystemLog.user_id == user_id)
        if date_from:
            stmt = stmt.where(SystemLog.created_at >= date_from)
        if date_to:
            stmt = stmt.where(SystemLog.created_at <= date_to)
        result = await self.db.execute(stmt.order_by(SystemLog.created_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all())
