from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.alert import AlertDetailResponse, AlertResponse, AlertTransitionRequest, AlertTransitionResponse
from app.application.services import AlertWorkflowService
from app.core.database import get_db
from app.domain.enums import AlertSeverity, AlertStatus
from app.infrastructure.models import User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    status_filter: AlertStatus | None = Query(default=None, alias="status"),
    plant_id: int | None = Query(default=None),
    severity: AlertSeverity | None = Query(default=None),
    metric: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await AlertWorkflowService(db).list_for_user(
        user_id=current_user.id,
        status_filter=status_filter,
        plant_id=plant_id,
        severity=severity,
        metric=metric,
        limit=limit,
        offset=offset,
    )


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await AlertWorkflowService(db).get_for_user(user_id=current_user.id, alert_id=alert_id)


@router.post("/{alert_id}/transition", response_model=AlertTransitionResponse)
async def transition_alert(
    alert_id: int,
    payload: AlertTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, transition = await AlertWorkflowService(db).transition(
        user_id=current_user.id,
        alert_id=alert_id,
        to_status=payload.to_status,
        note=payload.note,
    )
    return transition
