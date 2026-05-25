from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import joblib

from app.ml import FEATURE_COLUMNS, METADATA_PATH, MODEL_PATH


class MLConditionService:
    _cached_model = None
    _cached_metadata: dict[str, object] = {}
    _cached_load_error: str | None = None
    _cached_paths: tuple[Path, Path] | None = None

    def __init__(
        self,
        *,
        model_path: Path | None = None,
        metadata_path: Path | None = None,
    ) -> None:
        self.model_path = Path(model_path or MODEL_PATH)
        self.metadata_path = Path(metadata_path or METADATA_PATH)
        self._model = None
        self._metadata: dict[str, object] = {}
        self._load_error: str | None = None
        self._load_artifacts()

    @property
    def model_available(self) -> bool:
        return self._model is not None

    @property
    def metadata(self) -> dict[str, object]:
        return self._metadata

    def _load_artifacts(self) -> None:
        paths = (self.model_path, self.metadata_path)
        if MLConditionService._cached_paths == paths:
            self._model = MLConditionService._cached_model
            self._metadata = MLConditionService._cached_metadata
            self._load_error = MLConditionService._cached_load_error
            return

        if not self.model_path.exists():
            self._load_error = f"Model file not found: {self.model_path.name}"
            MLConditionService._cached_paths = paths
            MLConditionService._cached_model = None
            MLConditionService._cached_metadata = {}
            MLConditionService._cached_load_error = self._load_error
            return
        try:
            self._model = joblib.load(self.model_path)
            if self.metadata_path.exists():
                self._metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._model = None
            self._metadata = {}
            self._load_error = str(exc)
        finally:
            MLConditionService._cached_paths = paths
            MLConditionService._cached_model = self._model
            MLConditionService._cached_metadata = self._metadata
            MLConditionService._cached_load_error = self._load_error

    @staticmethod
    def _safe_result(model_available: bool = False) -> dict[str, object]:
        return {
            "ml_prediction": None,
            "ml_confidence": None,
            "class_probabilities": {},
            "model_available": model_available,
        }

    def predict_condition(self, features: Mapping[str, float | int | None]) -> dict[str, object]:
        if not self.model_available:
            return self._safe_result(model_available=False)

        try:
            vector = [[float(features.get(feature_name) or 0.0) for feature_name in FEATURE_COLUMNS]]
            prediction = str(self._model.predict(vector)[0])
            class_probabilities: dict[str, float] = {}
            confidence: float | None = None

            if hasattr(self._model, "predict_proba"):
                probabilities = self._model.predict_proba(vector)[0]
                labels = [str(label) for label in getattr(self._model, "classes_", [])]
                class_probabilities = {
                    label: round(float(probability), 4)
                    for label, probability in zip(labels, probabilities, strict=False)
                }
                confidence = round(max(class_probabilities.values()), 4) if class_probabilities else None

            return {
                "ml_prediction": prediction,
                "ml_confidence": confidence,
                "class_probabilities": class_probabilities,
                "model_available": True,
            }
        except Exception:
            return self._safe_result(model_available=False)
