from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.sensor import SensorCreate, SensorOut
from app.services import sensor_service

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("", response_model=SensorOut)
def create_sensor(
    data: SensorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SensorOut:
    return sensor_service.create_sensor(db, user, data)


@router.get("", response_model=List[SensorOut])
def list_sensors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[SensorOut]:
    return sensor_service.list_sensors(db, user)


@router.post("/{sensor_id}/attach/{plant_id}", response_model=SensorOut)
def attach(
    sensor_id: int,
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SensorOut:
    return sensor_service.attach_sensor(db, user, sensor_id, plant_id)


@router.post("/{sensor_id}/detach", response_model=SensorOut)
def detach(
    sensor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SensorOut:
    return sensor_service.detach_sensor(db, user, sensor_id)
