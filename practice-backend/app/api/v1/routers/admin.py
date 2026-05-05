from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.application.schemas.admin import (
    AdminAlertResponse,
    AdminSensorResponse,
    AdminUserResponse,
    SystemLogResponse,
)
from app.application.services import AdminService
from app.core.database import get_db
from app.domain.enums import AlertSeverity, AlertStatus

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).users(limit=limit, offset=offset)


@router.get("/sensors", response_model=list[AdminSensorResponse])
async def list_sensors(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).sensors(limit=limit, offset=offset)


@router.get("/alerts", response_model=list[AdminAlertResponse])
async def list_alerts(
    status: AlertStatus | None = Query(default=None),
    severity: AlertSeverity | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).alerts(limit=limit, offset=offset, status=status, severity=severity)


@router.get("/logs", response_model=list[SystemLogResponse])
async def list_logs(
    event_type: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).system_logs(
        limit=limit,
        offset=offset,
        event_type=event_type,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
