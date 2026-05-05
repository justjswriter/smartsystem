from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plant import Plant


class PlantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plant_id: int) -> Optional[Plant]:
        return self.db.get(Plant, plant_id)

    def get_by_id_for_user(
        self, plant_id: int, user_id: int, include_inactive: bool = False
    ) -> Optional[Plant]:
        q = select(Plant).where(Plant.id == plant_id, Plant.user_id == user_id)
        if not include_inactive:
            q = q.where(Plant.is_active.is_(True))
        return self.db.execute(q).scalar_one_or_none()

    def list_for_user(self, user_id: int, only_active: bool = True) -> List[Plant]:
        q = select(Plant).where(Plant.user_id == user_id)
        if only_active:
            q = q.where(Plant.is_active.is_(True))
        return list(self.db.execute(q).scalars().all())

    def create(
        self,
        user_id: int,
        name: str,
        species: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Plant:
        p = Plant(
            user_id=user_id,
            name=name,
            species=species,
            location=location,
            description=description,
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def save(self, plant: Plant) -> Plant:
        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)
        return plant

    def soft_delete(self, plant: Plant) -> None:
        plant.is_active = False
        self.save(plant)
