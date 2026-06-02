from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AlertSeverity, AlertStatus
from app.infrastructure.repositories import AlertRepository, SystemLogRepository
from app.infrastructure.services.event_bus import event_bus

ALLOWED_TRANSITIONS: dict[AlertStatus, set[AlertStatus]] = {
    AlertStatus.CREATED: {AlertStatus.VIEWED, AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED},
    AlertStatus.VIEWED: {AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED},
    AlertStatus.ACKNOWLEDGED: {AlertStatus.RESOLVED},
    AlertStatus.RESOLVED: {AlertStatus.CLOSED},
    AlertStatus.CLOSED: set(),
}


class AlertWorkflowService:
    def __init__(self, db: AsyncSession):
        self.alert_repo = AlertRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def list_for_user(
        self,
        *,
        user_id: int,
        status_filter: AlertStatus | None,
        plant_id: int | None,
        severity: AlertSeverity | None,
        metric: str | None,
        limit: int,
        offset: int,
    ):
        return await self.alert_repo.list_for_user(
            user_id=user_id,
            status=status_filter,
            plant_id=plant_id,
            severity=severity,
            metric=metric,
            limit=limit,
            offset=offset,
        )

    async def get_for_user(self, *, user_id: int, alert_id: int):
        alert = await self.alert_repo.get_for_user(alert_id, user_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return alert

    async def transition(self, *, user_id: int, alert_id: int, to_status: AlertStatus, note: str | None):
        alert = await self.get_for_user(user_id=user_id, alert_id=alert_id)
        from_status = alert.status
        if to_status not in ALLOWED_TRANSITIONS[from_status]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid transition: {from_status.value} -> {to_status.value}",
            )

        await self.alert_repo.update_status(alert, to_status)
        transition = await self.alert_repo.add_transition(
            alert_id=alert_id,
            from_status=from_status,
            to_status=to_status,
            user_id=user_id,
            note=note,
        )
        await self.log_repo.create(
            event_type="alert_transition",
            message=f"Alert {alert_id} {from_status.value}->{to_status.value}",
            user_id=user_id,
            payload={"alert_id": alert_id, "from": from_status.value, "to": to_status.value},
        )
        await event_bus.publish(
            f"alerts:{user_id}",
            {"event": "alert_transition", "alert_id": alert_id, "from": from_status.value, "to": to_status.value},
        )
        return alert, transition
