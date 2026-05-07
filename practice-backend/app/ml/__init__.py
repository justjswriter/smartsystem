from pathlib import Path

ML_DIR = Path(__file__).resolve().parent
DATASET_PATH = ML_DIR / "training_dataset.csv"
MODEL_PATH = ML_DIR / "plant_condition_model.joblib"
METADATA_PATH = ML_DIR / "model_metadata.json"

FEATURE_COLUMNS = [
    "moisture",
    "temperature",
    "humidity",
    "light",
    "moisture_trend",
    "temperature_trend",
    "humidity_trend",
    "light_trend",
]

LABELS = ["normal", "attention", "critical"]

