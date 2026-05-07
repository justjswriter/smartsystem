from __future__ import annotations

import json

import joblib
from sklearn.ensemble import RandomForestClassifier

from app.application.services.ml_condition_service import MLConditionService
from app.ml import FEATURE_COLUMNS


SAMPLE_FEATURES = {
    "moisture": 24.0,
    "temperature": 34.0,
    "humidity": 28.0,
    "light": 180.0,
    "moisture_trend": -7.0,
    "temperature_trend": 4.0,
    "humidity_trend": -5.0,
    "light_trend": -90.0,
}


def _create_temp_model(tmp_path):
    x_train = [
        [55.0, 24.0, 50.0, 500.0, 1.0, 0.0, 1.0, 10.0],
        [48.0, 26.0, 45.0, 450.0, -2.0, 1.0, -1.0, -20.0],
        [25.0, 33.0, 28.0, 180.0, -8.0, 4.0, -5.0, -90.0],
        [29.0, 31.0, 32.0, 220.0, -6.0, 3.0, -2.0, -40.0],
        [8.0, 42.0, 12.0, 70.0, -16.0, 8.0, -10.0, -200.0],
        [12.0, 39.0, 18.0, 90.0, -12.0, 6.0, -8.0, -160.0],
    ]
    y_train = [
        "normal",
        "normal",
        "attention",
        "attention",
        "critical",
        "critical",
    ]
    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(x_train, y_train)

    model_path = tmp_path / "plant_condition_model.joblib"
    metadata_path = tmp_path / "model_metadata.json"
    joblib.dump(model, model_path)
    metadata_path.write_text(
        json.dumps(
            {
                "model_type": "RandomForestClassifier",
                "features": FEATURE_COLUMNS,
                "labels": ["normal", "attention", "critical"],
                "accuracy": 1.0,
                "training_date": "2026-05-07T00:00:00+00:00",
                "dataset_size": len(x_train),
            }
        ),
        encoding="utf-8",
    )
    return model_path, metadata_path


def test_ml_service_fails_safely_when_model_is_missing(tmp_path):
    service = MLConditionService(
        model_path=tmp_path / "missing.joblib",
        metadata_path=tmp_path / "missing.json",
    )
    result = service.predict_condition(SAMPLE_FEATURES)
    assert result["model_available"] is False
    assert result["ml_prediction"] is None
    assert result["ml_confidence"] is None
    assert result["class_probabilities"] == {}


def test_ml_service_predicts_supported_label(tmp_path):
    model_path, metadata_path = _create_temp_model(tmp_path)
    service = MLConditionService(model_path=model_path, metadata_path=metadata_path)
    result = service.predict_condition(SAMPLE_FEATURES)
    assert result["model_available"] is True
    assert result["ml_prediction"] in {"normal", "attention", "critical"}
    assert isinstance(result["class_probabilities"], dict)
    assert {"normal", "attention", "critical"}.issubset(result["class_probabilities"].keys())
    assert 0.0 <= float(result["ml_confidence"]) <= 1.0
