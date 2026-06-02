from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.alert import AlertListResponse, AlertOut
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status enum name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertListResponse:
    return alert_service.list_alerts(db, user, status, limit, offset)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertOut:
    return alert_service.get_alert(db, user, alert_id)


@router.post("/{alert_id}/view", response_model=AlertOut)
def view(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertOut:
    return alert_service.set_viewed(db, user, alert_id)


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def ack(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertOut:
    return alert_service.acknowledge(db, user, alert_id)


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertOut:
    return alert_service.resolve_alert(db, user, alert_id)


@router.post("/{alert_id}/close", response_model=AlertOut)
def close(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AlertOut:
    return alert_service.close_alert(db, user, alert_id)
