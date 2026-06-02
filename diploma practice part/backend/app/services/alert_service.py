from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.alert import AlertStatus
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertListResponse, AlertOut


def _get_alert_for_user(db: Session, user: User, alert_id: int):
    a = AlertRepository(db).get_for_user(alert_id, user.id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    return a


def list_alerts(
    db: Session,
    user: User,
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> AlertListResponse:
    items, total = AlertRepository(db).list_for_user(
        user.id, status_filter=status_filter, limit=limit, offset=offset
    )
    return AlertListResponse(
        total=total, items=[AlertOut.model_validate(a) for a in items]
    )


def get_alert(db: Session, user: User, alert_id: int) -> AlertOut:
    a = _get_alert_for_user(db, user, alert_id)
    return AlertOut.model_validate(a)


def set_viewed(db: Session, user: User, alert_id: int) -> AlertOut:
    a = _get_alert_for_user(db, user, alert_id)
    if a.status == AlertStatus.created:
        a.status = AlertStatus.viewed
    return AlertOut.model_validate(AlertRepository(db).save(a))


def acknowledge(db: Session, user: User, alert_id: int) -> AlertOut:
    a = _get_alert_for_user(db, user, alert_id)
    a.status = AlertStatus.acknowledged
    return AlertOut.model_validate(AlertRepository(db).save(a))


def resolve_alert(db: Session, user: User, alert_id: int) -> AlertOut:
    a = _get_alert_for_user(db, user, alert_id)
    a.status = AlertStatus.resolved
    a.resolved_at = datetime.now(timezone.utc)
    return AlertOut.model_validate(AlertRepository(db).save(a))


def close_alert(db: Session, user: User, alert_id: int) -> AlertOut:
    a = _get_alert_for_user(db, user, alert_id)
    a.status = AlertStatus.closed
    if a.resolved_at is None:
        a.resolved_at = datetime.now(timezone.utc)
    return AlertOut.model_validate(AlertRepository(db).save(a))
