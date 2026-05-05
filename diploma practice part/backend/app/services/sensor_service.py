from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.plant_repository import PlantRepository
from app.repositories.sensor_repository import SensorRepository
from app.schemas.sensor import SensorCreate, SensorOut
from app.services import plant_service


def create_sensor(db: Session, user: User, data: SensorCreate) -> SensorOut:
    repo = SensorRepository(db)
    if repo.get_by_device_id(data.device_id):
        raise HTTPException(status_code=400, detail="Device ID already exists")
    plant_id = data.plant_id
    if plant_id is not None:
        plant_service.get_plant_entity_for_user(db, user, plant_id, allow_inactive=False)
    s = repo.create(
        device_id=data.device_id,
        plant_id=plant_id,
        sensor_type=data.sensor_type,
        status=data.status,
    )
    return SensorOut.model_validate(s)


def list_sensors(db: Session, user: User) -> List[SensorOut]:
    repo = SensorRepository(db)
    rows = repo.list_for_user(user.id)
    return [SensorOut.model_validate(s) for s in rows]


def attach_sensor(
    db: Session, user: User, sensor_id: int, plant_id: int
) -> SensorOut:
    pl_repo = PlantRepository(db)
    s_repo = SensorRepository(db)
    plant = pl_repo.get_by_id_for_user(plant_id, user.id, include_inactive=False)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    s = s_repo.get_by_id(sensor_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sensor not found")
    s.plant_id = plant_id
    s = s_repo.save(s)
    return SensorOut.model_validate(s)


def detach_sensor(db: Session, user: User, sensor_id: int) -> SensorOut:
    s_repo = SensorRepository(db)
    s = s_repo.get_by_id(sensor_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sensor not found")
    if s.plant_id is not None:
        plant = PlantRepository(db).get_by_id_for_user(s.plant_id, user.id, include_inactive=True)
        if not plant:
            raise HTTPException(
                status_code=403, detail="Not allowed to modify this sensor"
            )
    s.plant_id = None
    s = s_repo.save(s)
    return SensorOut.model_validate(s)
