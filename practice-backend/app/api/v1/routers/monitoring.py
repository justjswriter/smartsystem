from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.dashboard import DashboardResponse
from app.application.services import MonitoringService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/plants/{plant_id}", response_model=DashboardResponse)
async def get_plant_dashboard(
    plant_id: int,
    hours: int = Query(default=24, ge=1, le=24 * 30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MonitoringService(db)
    return await service.get_dashboard(user_id=current_user.id, plant_id=plant_id, hours=hours)
