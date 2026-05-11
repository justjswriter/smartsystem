from datetime import datetime, timezone

from app.application.schemas.dashboard import DashboardPoint
from app.application.services.ml_condition_service import MLConditionService
from app.application.services.plant_condition_service import PlantConditionService


def point(**overrides):
    payload = {
        "recorded_at": datetime.now(timezone.utc),
        "moisture": 45.0,
        "temperature": 24.0,
        "humidity": 45.0,
        "light": 500.0,
    }
    payload.update(overrides)
    return DashboardPoint(**payload)


def test_condition_insufficient_data():
    condition = PlantConditionService().evaluate(current=None, history=[])
    assert condition.condition_status == "insufficient_data"
    assert condition.health_score is None


def test_condition_normal():
    history = [point() for _ in range(8)]
    condition = PlantConditionService().evaluate(current=history[-1], history=history)
    assert condition.condition_status == "normal"
    assert condition.health_score == 100


def test_condition_critical_for_bad_sensor_values():
    current = point(moisture=5.0, temperature=42.0, humidity=15.0, light=50.0)
    condition = PlantConditionService().evaluate(current=current, history=[current])
    assert condition.condition_status == "critical"
    assert "low_moisture" in condition.risk_factors


def test_dashboard_condition_works_without_model(tmp_path):
    service = PlantConditionService(
        ml_service=MLConditionService(
            model_path=tmp_path / "missing.joblib",
            metadata_path=tmp_path / "missing.json",
        )
    )
    history = [point() for _ in range(6)]
    condition = service.evaluate(current=history[-1], history=history)
    assert condition.condition_status == "normal"
    assert condition.analysis_method == "rule_based"
    assert condition.ml_prediction is None
    assert condition.class_probabilities == {}


class StubMLService:
    def __init__(self, prediction: str, confidence: float):
        self.prediction = prediction
        self.confidence = confidence
        self.model_available = True

    def predict_condition(self, _features):
        return {
            "ml_prediction": self.prediction,
            "ml_confidence": self.confidence,
            "class_probabilities": {
                "normal": 0.03,
                "attention": 0.06,
                "critical": 0.91,
            },
            "model_available": True,
        }


def test_dashboard_condition_includes_ml_fields_when_model_exists():
    current = point(moisture=5.0, temperature=42.0, humidity=15.0, light=50.0)
    service = PlantConditionService(ml_service=StubMLService(prediction="critical", confidence=0.91))
    condition = service.evaluate(current=current, history=[current, point(moisture=20.0, temperature=35.0, humidity=25.0, light=150.0)])
    assert condition.analysis_method == "hybrid_rule_based_and_ml"
    assert condition.ml_prediction == "critical"
    assert condition.ml_confidence == 0.91
    assert condition.class_probabilities["critical"] == 0.91
