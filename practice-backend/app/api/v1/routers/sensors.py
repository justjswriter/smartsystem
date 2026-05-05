from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.sensor import SensorAttachRequest, SensorCreate, SensorProvisionResponse, SensorResponse
from app.application.services import SensorService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("", response_model=SensorProvisionResponse)
async def register_sensor(
    payload: SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sensor, token = await SensorService(db).create(payload=payload, current_user=current_user)
    return SensorProvisionResponse(sensor=sensor, device_token=token)


@router.get("", response_model=list[SensorResponse])
async def list_sensors(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SensorService(db).list(current_user=current_user, limit=limit, offset=offset)


@router.post("/{sensor_id}/attach", response_model=SensorResponse)
async def attach_sensor(
    sensor_id: int,
    payload: SensorAttachRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SensorService(db).attach(
        user_id=current_user.id, sensor_id=sensor_id, plant_id=payload.plant_id
    )


@router.post("/{sensor_id}/detach", response_model=SensorResponse)
async def detach_sensor(
    sensor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SensorService(db).detach(user_id=current_user.id, sensor_id=sensor_id)


@router.post("/{sensor_id}/rotate-token", response_model=SensorProvisionResponse)
async def rotate_sensor_token(
    sensor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sensor, token = await SensorService(db).rotate_token(current_user=current_user, sensor_id=sensor_id)
    return SensorProvisionResponse(sensor=sensor, device_token=token)
