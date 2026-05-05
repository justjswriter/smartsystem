from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        plant_id: int,
        text: str,
        explanation: Optional[str],
        alert_id: Optional[int] = None,
        commit: bool = True,
    ) -> Recommendation:
        r = Recommendation(
            plant_id=plant_id,
            alert_id=alert_id,
            text=text,
            explanation=explanation,
        )
        self.db.add(r)
        if commit:
            self.db.commit()
            self.db.refresh(r)
        else:
            self.db.flush()
            self.db.refresh(r)
        return r

    def list_recent_for_plant(
        self, plant_id: int, limit: int = 5
    ) -> List[Recommendation]:
        q = (
            select(Recommendation)
            .where(Recommendation.plant_id == plant_id)
            .order_by(desc(Recommendation.created_at))
            .limit(limit)
        )
        return list(self.db.execute(q).scalars().all())
