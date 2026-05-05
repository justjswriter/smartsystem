from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.plant import PlantCreate, PlantOut, PlantUpdate
from app.schemas.reading import ReadingListItem, ReadingOut
from app.schemas.dashboard import PlantDashboardOut
from app.schemas.recommendation import RecommendationListOut
from app.services import plant_service, reading_service, dashboard_service, recommendation_service

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("", response_model=PlantOut)
def create_plant(
    data: PlantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlantOut:
    return plant_service.create_plant(db, user, data)


@router.get("", response_model=List[PlantOut])
def list_plants(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[PlantOut]:
    return plant_service.list_plants(db, user)


# Sub-routes (more specific) before the bare /{plant_id} handler
@router.get("/{plant_id}/readings", response_model=List[ReadingListItem])
def get_readings(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[ReadingListItem]:
    return reading_service.list_readings(db, user, plant_id, limit, offset)


@router.get("/{plant_id}/latest", response_model=ReadingOut)
def get_latest(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReadingOut:
    return reading_service.get_latest(db, user, plant_id)


@router.get("/{plant_id}/dashboard", response_model=PlantDashboardOut)
def plant_dashboard(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlantDashboardOut:
    return dashboard_service.get_plant_dashboard(db, user, plant_id)


@router.get("/{plant_id}/recommendations", response_model=RecommendationListOut)
def plant_recommendations(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecommendationListOut:
    return recommendation_service.list_recent_recommendations(
        db, user, plant_id, limit=10
    )


@router.get("/{plant_id}", response_model=PlantOut)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlantOut:
    return plant_service.get_plant(db, user, plant_id)


@router.put("/{plant_id}", response_model=PlantOut)
def update_plant(
    plant_id: int,
    data: PlantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PlantOut:
    return plant_service.update_plant(db, user, plant_id, data)


@router.delete("/{plant_id}", status_code=204)
def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    plant_service.soft_delete_plant(db, user, plant_id)
