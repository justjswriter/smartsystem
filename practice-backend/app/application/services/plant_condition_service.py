from __future__ import annotations

from datetime import datetime, timezone

from app.application.schemas.dashboard import DashboardPoint, PlantConditionResponse
from app.application.services.ml_condition_service import MLConditionService
from app.core.config import settings


class PlantConditionService:
    """Explainable hybrid condition scoring with rule-based safety baseline."""

    def __init__(self, ml_service: MLConditionService | None = None) -> None:
        self.ml_service = ml_service or MLConditionService()

    def evaluate(self, *, current: DashboardPoint | None, history: list[DashboardPoint]) -> PlantConditionResponse:
        if not current:
            return PlantConditionResponse(
                condition_status="insufficient_data",
                health_score=None,
                risk_factors=[],
                confidence=0.0,
                explanation="No sensor samples are available yet. Attach a sensor and send telemetry to evaluate the plant.",
                analysis_method="hybrid_rule_based_and_ml" if self.ml_service.model_available else "rule_based",
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
        ml_result = self._predict_ml(current=current, history=history)
        analysis_method = (
            "hybrid_rule_based_and_ml"
            if ml_result["model_available"] and ml_result["ml_prediction"]
            else "rule_based"
        )
        if ml_result["ml_prediction"]:
            explanation = self._merge_explanations(
                explanation=explanation,
                rule_based_status=status,
                ml_prediction=str(ml_result["ml_prediction"]),
                ml_confidence=ml_result["ml_confidence"],
            )
        return PlantConditionResponse(
            condition_status=status,
            health_score=score,
            risk_factors=risks,
            confidence=confidence,
            explanation=explanation,
            ml_prediction=ml_result["ml_prediction"],
            ml_confidence=ml_result["ml_confidence"],
            class_probabilities=ml_result["class_probabilities"],
            analysis_method=analysis_method,
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

    def _predict_ml(self, *, current: DashboardPoint, history: list[DashboardPoint]) -> dict[str, object]:
        required_values = [current.moisture, current.temperature, current.humidity, current.light]
        if any(value is None for value in required_values):
            return {
                "ml_prediction": None,
                "ml_confidence": None,
                "class_probabilities": {},
                "model_available": self.ml_service.model_available,
            }
        return self.ml_service.predict_condition(self._build_ml_features(current=current, history=history))

    def _build_ml_features(self, *, current: DashboardPoint, history: list[DashboardPoint]) -> dict[str, float]:
        return {
            "moisture": float(current.moisture or 0.0),
            "temperature": float(current.temperature or 0.0),
            "humidity": float(current.humidity or 0.0),
            "light": float(current.light or 0.0),
            "moisture_trend": self._trend_value(history, "moisture"),
            "temperature_trend": self._trend_value(history, "temperature"),
            "humidity_trend": self._trend_value(history, "humidity"),
            "light_trend": self._trend_value(history, "light"),
        }

    @staticmethod
    def _trend_value(history: list[DashboardPoint], field_name: str) -> float:
        values = [
            float(value)
            for point in history
            if (value := getattr(point, field_name)) is not None
        ]
        if len(values) < 2:
            return 0.0
        return round(values[-1] - values[0], 2)

    @staticmethod
    def _merge_explanations(
        *,
        explanation: str,
        rule_based_status: str,
        ml_prediction: str,
        ml_confidence: float | None,
    ) -> str:
        if ml_confidence is None:
            confidence_text = "unknown confidence"
        else:
            confidence_text = f"{round(ml_confidence * 100)}% confidence"

        if ml_prediction == rule_based_status:
            return (
                f"{explanation} The supporting Random Forest model also predicts "
                f"{ml_prediction} with {confidence_text}."
            )

        return (
            f"{explanation} The supporting Random Forest model predicts {ml_prediction} "
            f"with {confidence_text}, which differs from the rule-based result. "
            "Rule-based status remains primary for safety."
        )
