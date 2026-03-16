from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AlertStatus
from app.infrastructure.models import Alert, AlertTransition


class AlertRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> Alert:
        alert = Alert(**payload)
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def list_for_user(
        self,
        *,
        user_id: int,
        status: AlertStatus | None = None,
        plant_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Alert]:
        stmt = select(Alert).where(Alert.user_id == user_id)
        if status:
            stmt = stmt.where(Alert.status == status)
        if plant_id:
            stmt = stmt.where(Alert.plant_id == plant_id)
        result = await self.db.execute(stmt.order_by(Alert.created_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def list_all(self, *, limit: int, offset: int) -> list[Alert]:
        result = await self.db.execute(
            select(Alert).order_by(Alert.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_for_user(self, alert_id: int, user_id: int) -> Alert | None:
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, alert_id: int) -> Alert | None:
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    async def find_open_by_metric(self, *, plant_id: int, metric: str) -> Alert | None:
        result = await self.db.execute(
            select(Alert).where(
                Alert.plant_id == plant_id,
                Alert.metric == metric,
                Alert.status.in_(
                    [AlertStatus.CREATED, AlertStatus.VIEWED, AlertStatus.ACKNOWLEDGED]
                ),
            )
        )
        return result.scalar_one_or_none()

    async def update_status(self, alert: Alert, to_status: AlertStatus) -> Alert:
        alert.status = to_status
        if to_status in (AlertStatus.RESOLVED, AlertStatus.CLOSED):
            alert.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def add_transition(
        self, *, alert_id: int, from_status: AlertStatus, to_status: AlertStatus, user_id: int, note: str | None
    ) -> AlertTransition:
        transition = AlertTransition(
            alert_id=alert_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=user_id,
            note=note,
        )
        self.db.add(transition)
        await self.db.commit()
        await self.db.refresh(transition)
        return transition
