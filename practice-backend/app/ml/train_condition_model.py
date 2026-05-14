from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import random

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.domain.plant_knowledge import resolve_plant_profile
from app.ml import DATASET_PATH, FEATURE_COLUMNS, LABELS, METADATA_PATH, MODEL_PATH


PROFILE = resolve_plant_profile()
MOISTURE = PROFILE.thresholds["moisture"]
TEMPERATURE = PROFILE.thresholds["temperature"]
HUMIDITY = PROFILE.thresholds["humidity"]
LIGHT = PROFILE.thresholds["light"]


def _uniform(rng: random.Random, start: float, stop: float) -> float:
    return round(rng.uniform(start, stop), 2)


def _base_normal_row(rng: random.Random) -> dict[str, float]:
    return {
        "moisture": _uniform(rng, MOISTURE.optimal_min or 45.0, MOISTURE.optimal_max or 65.0),
        "temperature": _uniform(rng, TEMPERATURE.optimal_min or 20.0, TEMPERATURE.optimal_max or 27.0),
        "humidity": _uniform(rng, HUMIDITY.optimal_min or 50.0, HUMIDITY.optimal_max or 70.0),
        "light": _uniform(rng, LIGHT.optimal_min or 45.0, LIGHT.optimal_max or 180.0),
        "moisture_trend": _uniform(rng, -4.0, 4.0),
        "temperature_trend": _uniform(rng, -2.0, 2.0),
        "humidity_trend": _uniform(rng, -4.0, 4.0),
        "light_trend": _uniform(rng, -20.0, 20.0),
    }


def _attention_row(rng: random.Random) -> dict[str, float]:
    row = _base_normal_row(rng)
    scenario = rng.choice(
        [
            "moderate_low_moisture",
            "moderate_high_temperature",
            "moderate_low_humidity",
            "moderate_low_light",
            "combined_mild_stress",
        ]
    )
    if scenario == "moderate_low_moisture":
        row["moisture"] = _uniform(rng, 20.0, (MOISTURE.min or 35.0) - 2.0)
        row["moisture_trend"] = _uniform(rng, -14.0, -5.0)
    elif scenario == "moderate_high_temperature":
        row["temperature"] = _uniform(rng, (TEMPERATURE.max or 30.0) + 1.0, 36.0)
        row["temperature_trend"] = _uniform(rng, 3.0, 8.0)
    elif scenario == "moderate_low_humidity":
        row["humidity"] = _uniform(rng, 25.0, (HUMIDITY.min or 40.0) - 2.0)
        row["humidity_trend"] = _uniform(rng, -12.0, -3.0)
    elif scenario == "moderate_low_light":
        row["light"] = _uniform(rng, 22.0, (LIGHT.min or 40.0) - 2.0)
        row["light_trend"] = _uniform(rng, -35.0, -8.0)
    else:
        row["moisture"] = _uniform(rng, 25.0, (MOISTURE.min or 35.0) - 1.0)
        row["temperature"] = _uniform(rng, (TEMPERATURE.optimal_max or 27.0) + 1.0, 34.0)
        row["humidity"] = _uniform(rng, 25.0, (HUMIDITY.min or 40.0) - 4.0)
        row["light"] = _uniform(rng, 20.0, (LIGHT.min or 40.0) - 3.0)
        row["moisture_trend"] = _uniform(rng, -10.0, -3.0)
        row["temperature_trend"] = _uniform(rng, 2.5, 6.0)
    return row


def _critical_row(rng: random.Random) -> dict[str, float]:
    row = _base_normal_row(rng)
    scenario = rng.choice(
        [
            "severe_low_moisture",
            "severe_high_temperature",
            "severe_low_humidity",
            "severe_low_light",
            "multiple_severe_stressors",
        ]
    )
    if scenario == "severe_low_moisture":
        row["moisture"] = _uniform(rng, 2.0, 18.0)
        row["moisture_trend"] = _uniform(rng, -24.0, -8.0)
    elif scenario == "severe_high_temperature":
        row["temperature"] = _uniform(rng, 37.0, 48.0)
        row["temperature_trend"] = _uniform(rng, 6.0, 12.0)
    elif scenario == "severe_low_humidity":
        row["humidity"] = _uniform(rng, 5.0, 20.0)
        row["humidity_trend"] = _uniform(rng, -18.0, -6.0)
    elif scenario == "severe_low_light":
        row["light"] = _uniform(rng, 1.0, 20.0)
        row["light_trend"] = _uniform(rng, -45.0, -12.0)
    else:
        row["moisture"] = _uniform(rng, 4.0, 22.0)
        row["temperature"] = _uniform(rng, 37.0, 45.0)
        row["humidity"] = _uniform(rng, 8.0, 24.0)
        row["light"] = _uniform(rng, 1.0, 22.0)
        row["moisture_trend"] = _uniform(rng, -20.0, -6.0)
        row["temperature_trend"] = _uniform(rng, 5.0, 11.0)
        row["humidity_trend"] = _uniform(rng, -16.0, -5.0)
        row["light_trend"] = _uniform(rng, -42.0, -10.0)
    return row


def generate_training_dataset(
    dataset_path: Path = DATASET_PATH,
    *,
    rows_per_class: int = 140,
    seed: int = 42,
) -> int:
    rng = random.Random(seed)
    rows: list[dict[str, float | str]] = []

    for _ in range(rows_per_class):
        rows.append({**_base_normal_row(rng), "label": "normal"})
        rows.append({**_attention_row(rng), "label": "attention"})
        rows.append({**_critical_row(rng), "label": "critical"})

    rng.shuffle(rows)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with dataset_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[*FEATURE_COLUMNS, "label"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def load_training_dataset(dataset_path: Path = DATASET_PATH) -> tuple[list[list[float]], list[str]]:
    features: list[list[float]] = []
    labels: list[str] = []
    with dataset_path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            features.append([float(row[column]) for column in FEATURE_COLUMNS])
            labels.append(str(row["label"]))
    return features, labels


def train_and_save_model(
    dataset_path: Path = DATASET_PATH,
    model_path: Path = MODEL_PATH,
    metadata_path: Path = METADATA_PATH,
) -> dict[str, object]:
    if not dataset_path.exists():
        generate_training_dataset(dataset_path)

    features, labels = load_training_dataset(dataset_path)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    model = RandomForestClassifier(
        n_estimators=240,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = float(accuracy_score(y_test, predictions))
    report = classification_report(y_test, predictions, digits=3)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    metadata = {
        "model_type": "RandomForestClassifier",
        "features": FEATURE_COLUMNS,
        "labels": LABELS,
        "accuracy": round(accuracy, 4),
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_size": len(features),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Dataset path: {dataset_path}")
    print(f"Model path: {model_path}")
    print(f"Metadata path: {metadata_path}")
    print(f"Dataset size: {len(features)}")
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification report:")
    print(report)

    return metadata


def main() -> None:
    train_and_save_model()


if __name__ == "__main__":
    main()
