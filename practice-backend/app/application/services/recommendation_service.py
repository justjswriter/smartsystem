from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories import RecommendationRepository


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.repo = RecommendationRepository(db)

    def _build_recommendation(self, metric: str, severity: str) -> tuple[str, str]:
        if metric == "moisture":
            return (
                "Increase watering schedule and re-check soil in 2-4 hours.",
                f"Soil moisture is below threshold (severity={severity}).",
            )
        if metric == "temperature":
            return (
                "Move the plant to a cooler area and reduce direct heat exposure.",
                f"Temperature exceeded healthy range (severity={severity}).",
            )
        if metric == "humidity":
            return (
                "Increase ambient humidity (humidifier or misting) and monitor trends.",
                f"Air humidity dropped below configured minimum (severity={severity}).",
            )
        if metric == "light":
            return (
                "Move the plant to a brighter location or add supplemental light.",
                f"Light level is below expected range (severity={severity}).",
            )
        return (
            "Check sensor calibration and inspect plant conditions manually.",
            f"Generic recommendation generated for metric={metric}, severity={severity}.",
        )

    async def create_for_alert(self, *, plant_id: int, alert_id: int, metric: str, severity: str):
        text, reason = self._build_recommendation(metric, severity)
        await self.repo.deactivate_for_plant(plant_id)
        return await self.repo.create(
            plant_id=plant_id,
            alert_id=alert_id,
            text=text,
            reason=reason,
        )
