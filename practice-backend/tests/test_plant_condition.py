from datetime import datetime, timezone

from app.application.schemas.dashboard import DashboardPoint
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
    assert "low_soil_moisture" in condition.risk_factors
