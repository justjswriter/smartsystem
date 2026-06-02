# AI Module: Random Forest Condition Classification

This document describes the supervised machine learning component added to the **final diploma prototype** for plant condition monitoring.

## Overview

The system now includes a **RandomForestClassifier** implemented with **scikit-learn**. The ML model supports the existing rule-based condition logic by providing an additional condition classification based on environmental sensor data and short-term trends.

The ML module is used for:

- plant condition classification
- AI-supported interpretation of sensor telemetry
- dashboard enrichment with prediction confidence and class probabilities

The ML module is **not** used for:

- plant disease diagnosis
- image recognition
- deep learning
- cloud AI or external AI APIs

## Model Type

- **Algorithm:** `RandomForestClassifier`
- **Learning type:** supervised machine learning
- **Purpose:** classify plant condition into:
  - `normal`
  - `attention`
  - `critical`

## Input Features

The model uses these features:

- `moisture`
- `temperature`
- `humidity`
- `light`
- `moisture_trend`
- `temperature_trend`
- `humidity_trend`
- `light_trend`

The trend features are derived from the change between earlier and later values in the recent dashboard history.

## Dataset

Training data is stored in:

- `practice-backend/app/ml/training_dataset.csv`

The dataset is an **expert-labeled synthetic environmental dataset** designed for diploma demonstration and technical validation. It reflects realistic indoor plant monitoring conditions:

- `normal`: healthy ranges and stable trends
- `attention`: one moderate deviation or moderate stress trend
- `critical`: severe deviation or multiple stress factors

## Safety and Explainability

The existing rule-based condition analysis remains in place and is still the **primary safety baseline**.

- rule-based scoring continues to produce:
  - `condition_status`
  - `health_score`
  - `risk_factors`
  - `confidence`
  - `explanation`
- the ML model provides:
  - `ml_prediction`
  - `ml_confidence`
  - `class_probabilities`
  - `analysis_method`

If the ML prediction differs from the rule-based result, the backend explanation explicitly states that the ML support differs and that the **rule-based status remains primary for safety**.

## Runtime Behavior

- If the trained model file is available, the dashboard returns `analysis_method = "hybrid_rule_based_and_ml"`.
- If the model file is missing or cannot be loaded, the system automatically falls back to `analysis_method = "rule_based"`.
- The ingest pipeline, alerts, and recommendations continue working even when the ML model is unavailable.

## Training Command

Run from:

```bash
cd /Users/zhalgassovasaniya/Downloads/macpworkcopy2/practice-backend
../.venv/bin/python -m app.ml.train_condition_model
```

This command:

- loads or generates the training dataset
- trains the Random Forest model
- prints accuracy and a classification report
- saves the trained model to:
  - `practice-backend/app/ml/plant_condition_model.joblib`
- saves metadata to:
  - `practice-backend/app/ml/model_metadata.json`

## Recommended Diploma Wording

Use wording like:

“The system implements a supervised machine learning module based on a Random Forest classifier for plant condition classification. The classifier analyzes environmental telemetry and short-term trends to predict whether plant condition is normal, requires attention, or is critical. For safety and explainability, the ML output is combined with the existing rule-based decision-support logic rather than replacing it.”
