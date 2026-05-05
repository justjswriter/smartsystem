from __future__ import annotations

from datetime import datetime, timezone

from app.application.schemas.dashboard import DashboardPoint, PlantConditionResponse
from app.core.config import settings


class PlantConditionService:
    """Explainable lightweight condition scoring for diploma MVP."""

    def evaluate(self, *, current: DashboardPoint | None, history: list[DashboardPoint]) -> PlantConditionResponse:
        if not current:
            return PlantConditionResponse(
                condition_status="insufficient_data",
                health_score=None,
                risk_factors=[],
                confidence=0.0,
                explanation="No sensor samples are available yet. Attach a sensor and send telemetry to evaluate the plant.",
            )

        penalties: list[tuple[str, int]] = []
        if current.moisture is not None and current.moisture < settings.MOISTURE_MIN:
            penalties.append(("low_soil_moisture", self._below_penalty(current.moisture, settings.MOISTURE_MIN)))
        if current.temperature is not None and current.temperature > settings.TEMPERATURE_MAX:
            penalties.append(("high_temperature", self._above_penalty(current.temperature, settings.TEMPERATURE_MAX)))
        if current.humidity is not None and current.humidity < settings.HUMIDITY_MIN:
            penalties.append(("low_air_humidity", self._below_penalty(current.humidity, settings.HUMIDITY_MIN)))
        if current.light is not None and current.light < settings.LIGHT_MIN:
            penalties.append(("low_light", self._below_penalty(current.light, settings.LIGHT_MIN)))

        trend_penalty, trend_factors = self._trend_penalty(history)
        score = max(0, min(100, 100 - sum(p for _, p in penalties) - trend_penalty))
        risks = [name for name, _ in penalties] + trend_factors
        status = "normal"
        if score < 50 or any(p >= 40 for _, p in penalties):
            status = "critical"
        elif score < 75 or risks:
            status = "attention"

        confidence = self._confidence(current.recorded_at, history)
        explanation = self._explain(status, score, risks, confidence)
        return PlantConditionResponse(
            condition_status=status,
            health_score=score,
            risk_factors=risks,
            confidence=confidence,
            explanation=explanation,
        )

    @staticmethod
    def _below_penalty(value: float, threshold: float) -> int:
        if value <= 0:
            return 50
        ratio = threshold / value
        return min(50, max(10, round((ratio - 1) * 35)))

    @staticmethod
    def _above_penalty(value: float, threshold: float) -> int:
        ratio = value / threshold
        return min(50, max(10, round((ratio - 1) * 45)))

    @staticmethod
    def _trend_penalty(history: list[DashboardPoint]) -> tuple[int, list[str]]:
        if len(history) < 4:
            return 0, []
        first = history[0]
        last = history[-1]
        factors: list[str] = []
        penalty = 0
        if first.moisture is not None and last.moisture is not None and last.moisture < first.moisture - 10:
            factors.append("declining_soil_moisture_trend")
            penalty += 8
        if first.temperature is not None and last.temperature is not None and last.temperature > first.temperature + 5:
            factors.append("rising_temperature_trend")
            penalty += 8
        return penalty, factors

    @staticmethod
    def _confidence(recorded_at: datetime, history: list[DashboardPoint]) -> float:
        sample_score = min(1.0, len(history) / 8)
        recorded = recorded_at
        if recorded.tzinfo is None:
            recorded = recorded.replace(tzinfo=timezone.utc)
        age_hours = max(0.0, (datetime.now(timezone.utc) - recorded).total_seconds() / 3600)
        freshness_score = max(0.2, 1 - min(age_hours / 24, 0.8))
        return round((sample_score * 0.6) + (freshness_score * 0.4), 2)

    @staticmethod
    def _explain(status: str, score: int, risks: list[str], confidence: float) -> str:
        if status == "normal":
            return f"Sensor values are within the configured healthy range. Health score is {score} with confidence {confidence}."
        if status == "critical":
            return f"Critical plant condition detected: {', '.join(risks)}. Health score is {score} with confidence {confidence}."
        return f"Plant requires attention because of {', '.join(risks)}. Health score is {score} with confidence {confidence}."
