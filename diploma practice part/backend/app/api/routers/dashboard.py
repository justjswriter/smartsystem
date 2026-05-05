from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryOut, PlantDashboardOut
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardSummaryOut:
    return dashboard_service.get_dashboard_summary(db, user)


@router.get("/plants/{plant_id}", response_model=PlantDashboardOut)
def plant_summary(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlantDashboardOut:
    return dashboard_service.get_plant_dashboard(db, user, plant_id)
