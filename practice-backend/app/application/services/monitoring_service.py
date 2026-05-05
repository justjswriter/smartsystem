from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.dashboard import DashboardPoint, DashboardResponse
from app.application.services.plant_condition_service import PlantConditionService
from app.infrastructure.repositories import PlantRepository, RecommendationRepository, SensorDataRepository


class MonitoringService:
    def __init__(self, db: AsyncSession):
        self.plant_repo = PlantRepository(db)
        self.sensor_data_repo = SensorDataRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.condition_service = PlantConditionService()

    async def get_dashboard(self, *, user_id: int, plant_id: int, hours: int) -> DashboardResponse:
        plant = await self.plant_repo.get_for_user(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

        current_data = await self.sensor_data_repo.latest_for_plant(plant_id)
        history_data = await self.sensor_data_repo.history_for_plant(plant_id, hours)

        current = (
            DashboardPoint(
                recorded_at=current_data.recorded_at,
                moisture=current_data.moisture,
                temperature=current_data.temperature,
                humidity=current_data.humidity,
                light=current_data.light,
            )
            if current_data
            else None
        )
        history = [
            DashboardPoint(
                recorded_at=item.recorded_at,
                moisture=item.moisture,
                temperature=item.temperature,
                humidity=item.humidity,
                light=item.light,
            )
            for item in history_data
        ]
        condition = self.condition_service.evaluate(current=current, history=history)
        active_recommendation = await self.recommendation_repo.active_for_plant(plant_id)
        return DashboardResponse(
            plant_id=plant_id,
            last_updated_at=current_data.recorded_at if current_data else None,
            current=current,
            history=history,
            condition=condition,
            active_recommendation=active_recommendation,
        )
