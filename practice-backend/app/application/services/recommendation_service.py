from datetime import timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.dashboard import DashboardPoint, PlantConditionResponse, RecommendationSummary
from app.domain.plant_knowledge import PlantProfile, resolve_plant_profile
from app.domain.plant_knowledge.types import IssueDefinition
from app.infrastructure.repositories import RecommendationRepository


class RecommendationService:
    LOCAL_TIME_OFFSET = timedelta(hours=5)
    NIGHT_START_HOUR = 20
    NIGHT_END_HOUR = 7

    def __init__(self, db: AsyncSession):
        self.repo = RecommendationRepository(db)

    def _build_recommendation(
        self,
        issue: IssueDefinition | None = None,
        *,
        metric: str | None = None,
        severity: str,
    ) -> tuple[str, str]:
        if issue:
            return (
                issue.advice.text.text("en"),
                f"{issue.advice.reason.text('en')} (severity={severity}).",
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
        plant_profile: PlantProfile | None = None,
    ) -> RecommendationSummary | None:
        if current is None:
            return None
        profile = plant_profile or resolve_plant_profile()

        candidates: list[tuple[int, IssueDefinition, str, str, str]] = []
        for issue in profile.issues.values():
            self._add_issue_candidate(candidates, current=current, issue=issue)

        if candidates:
            _, issue, severity, text, reason = max(candidates, key=lambda candidate: candidate[0])
            return RecommendationSummary(
                text=text,
                reason=reason,
                metric=issue.metric,
                severity=severity,
                source="current_condition",
            )

        return RecommendationSummary(
            text=profile.stable_advice.text.text("en"),
            reason=f"{profile.stable_advice.reason.text('en')} Health status is {condition.condition_status}.",
            metric="stable",
            severity="normal",
            source="current_condition",
        )

    def _add_issue_candidate(
        self,
        candidates: list[tuple[int, IssueDefinition, str, str, str]],
        *,
        current: DashboardPoint,
        issue: IssueDefinition,
    ) -> None:
        value = getattr(current, issue.metric, None)
        if value is None:
            return
        if issue.metric == "light" and issue.direction == "below" and self._is_night(current.recorded_at):
            return
        if issue.direction == "below":
            if value >= issue.threshold:
                return
            severity = self._severity_from_below_threshold(value=value, threshold=issue.threshold)
        elif issue.direction == "above":
            if value <= issue.threshold:
                return
            severity = self._severity_from_above_threshold(value=value, threshold=issue.threshold)
        else:
            return
        text, reason = self._build_recommendation(issue, severity=severity)
        candidates.append((self._current_priority(metric=issue.metric, severity=severity), issue, severity, text, reason))

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

    @staticmethod
    def _is_night(recorded_at) -> bool:
        recorded = recorded_at
        if recorded.tzinfo is None:
            recorded = recorded.replace(tzinfo=timezone.utc)
        local_hour = (recorded.astimezone(timezone.utc) + RecommendationService.LOCAL_TIME_OFFSET).hour
        return local_hour >= RecommendationService.NIGHT_START_HOUR or local_hour < RecommendationService.NIGHT_END_HOUR

    async def create_for_alert(
        self,
        *,
        plant_id: int,
        alert_id: int,
        metric: str,
        severity: str,
        issue_code: str | None = None,
        plant_profile: PlantProfile | None = None,
    ):
        profile = plant_profile or resolve_plant_profile()
        issue = profile.issues.get(issue_code or "") or next(
            (candidate for candidate in profile.issues.values() if candidate.metric == metric),
            None,
        )
        text, reason = self._build_recommendation(issue, metric=metric, severity=severity)
        await self.repo.deactivate_for_plant(plant_id)
        return await self.repo.create(
            plant_id=plant_id,
            alert_id=alert_id,
            text=text,
            reason=reason,
        )
