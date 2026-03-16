from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import Recommendation


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def deactivate_for_plant(self, plant_id: int) -> None:
        result = await self.db.execute(
            select(Recommendation).where(
                Recommendation.plant_id == plant_id, Recommendation.is_active.is_(True)
            )
        )
        for recommendation in result.scalars().all():
            recommendation.is_active = False
        await self.db.commit()

    async def create(self, *, plant_id: int, alert_id: int | None, text: str, reason: str) -> Recommendation:
        recommendation = Recommendation(
            plant_id=plant_id,
            alert_id=alert_id,
            text=text,
            reason=reason,
            is_active=True,
        )
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        return recommendation
