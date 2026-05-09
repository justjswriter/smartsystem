from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.dashboard import DashboardPoint, PlantConditionResponse, RecommendationSummary
from app.core.config import settings
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

    def build_current_recommendation(
        self,
        *,
        current: DashboardPoint | None,
        condition: PlantConditionResponse,
    ) -> RecommendationSummary | None:
        if current is None:
            return None

        candidates: list[tuple[int, str, str, str, str]] = []
        self._add_below_threshold_candidate(
            candidates,
            metric="moisture",
            value=current.moisture,
            threshold=settings.MOISTURE_MIN,
        )
        self._add_above_threshold_candidate(
            candidates,
            metric="temperature",
            value=current.temperature,
            threshold=settings.TEMPERATURE_MAX,
        )
        self._add_below_threshold_candidate(
            candidates,
            metric="humidity",
            value=current.humidity,
            threshold=settings.HUMIDITY_MIN,
        )
        self._add_below_threshold_candidate(
            candidates,
            metric="light",
            value=current.light,
            threshold=settings.LIGHT_MIN,
        )

        if candidates:
            _, metric, severity, text, reason = max(candidates, key=lambda candidate: candidate[0])
            return RecommendationSummary(
                text=text,
                reason=reason,
                metric=metric,
                severity=severity,
                source="current_condition",
            )

        return RecommendationSummary(
            text="Conditions are stable. Keep the current care routine and continue monitoring sensor trends.",
            reason=(
                f"Latest sensor values are within configured thresholds. "
                f"Health status is {condition.condition_status}."
            ),
            metric="stable",
            severity="normal",
            source="current_condition",
        )

    def _add_below_threshold_candidate(
        self,
        candidates: list[tuple[int, str, str, str, str]],
        *,
        metric: str,
        value: float | None,
        threshold: float,
    ) -> None:
        if value is None or value >= threshold:
            return
        severity = self._severity_from_below_threshold(value=value, threshold=threshold)
        text, reason = self._build_recommendation(metric, severity)
        candidates.append((self._current_priority(metric=metric, severity=severity), metric, severity, text, reason))

    def _add_above_threshold_candidate(
        self,
        candidates: list[tuple[int, str, str, str, str]],
        *,
        metric: str,
        value: float | None,
        threshold: float,
    ) -> None:
        if value is None or value <= threshold:
            return
        severity = self._severity_from_above_threshold(value=value, threshold=threshold)
        text, reason = self._build_recommendation(metric, severity)
        candidates.append((self._current_priority(metric=metric, severity=severity), metric, severity, text, reason))

    @staticmethod
    def _severity_from_below_threshold(*, value: float, threshold: float) -> str:
        if value <= 0:
            return "critical"
        return RecommendationService._severity_from_ratio(threshold / value)

    @staticmethod
    def _severity_from_above_threshold(*, value: float, threshold: float) -> str:
        return RecommendationService._severity_from_ratio(value / threshold)

    @staticmethod
    def _severity_from_ratio(ratio: float) -> str:
        if ratio >= 2.0:
            return "critical"
        if ratio >= 1.5:
            return "high"
        if ratio >= 1.2:
            return "medium"
        return "low"

    @staticmethod
    def _current_priority(*, metric: str, severity: str) -> int:
        severity_base = {
            "critical": 80,
            "high": 50,
            "medium": 35,
            "low": 20,
        }.get(severity, 0)
        metric_weight = {
            "moisture": 20,
            "temperature": 10,
            "humidity": 8,
            "light": 6,
        }.get(metric, 0)
        return severity_base + metric_weight

    async def create_for_alert(self, *, plant_id: int, alert_id: int, metric: str, severity: str):
        text, reason = self._build_recommendation(metric, severity)
        await self.repo.deactivate_for_plant(plant_id)
        return await self.repo.create(
            plant_id=plant_id,
            alert_id=alert_id,
            text=text,
            reason=reason,
        )
