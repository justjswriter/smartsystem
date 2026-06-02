# Final Verification Report (Functional Prototype)

This document summarizes the final pre-submission verification of the diploma system: **Developing a Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring**.

## Scope

- Backend API and database migration health
- Frontend production build
- Supervised ML training artifact generation
- End-to-end IoT ingest flow with device token authentication
- Dashboard condition/recommendation output
- Alerts and admin read-only endpoints
- SSE ownership access control

## Environment

- Backend: FastAPI + SQLAlchemy + Alembic
- AI module: scikit-learn RandomForestClassifier
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL (Docker Compose)

## Verification Steps and Results

1. **Database migration**
   - Command: `../.venv/bin/alembic upgrade head`
   - Result: success (latest schema applied)

2. **ML model training**
   - Command: `../.venv/bin/python -m app.ml.train_condition_model`
   - Dataset: `practice-backend/app/ml/training_dataset.csv`
   - Dataset size: `420`
   - Saved model: `practice-backend/app/ml/plant_condition_model.joblib`
   - Saved metadata: `practice-backend/app/ml/model_metadata.json`
   - Accuracy: `1.0000`

3. **Backend tests**
   - Command: `PYTHONPATH=. ../.venv/bin/pytest -q`
   - Result: `12 passed`

4. **Frontend build**
   - Command: `npm run build` (in `smart-plant-frontend`)
   - Result: pass

5. **IoT ingest authentication**
   - Valid request with `X-Device-Token`: accepted
   - Request without token: rejected with `401`

6. **Dashboard condition output**
   - Verified fields:
     - `current`
     - `condition.condition_status`
     - `condition.health_score`
     - `condition.risk_factors`
     - `condition.confidence`
     - `condition.explanation`
     - `condition.ml_prediction`
     - `condition.ml_confidence`
     - `condition.class_probabilities`
     - `condition.analysis_method`
     - `active_recommendation`

7. **Alerts**
   - Alert list returns generated alert items
   - Alert payload includes recommendation text
   - Alert detail includes transition history field (`transitions`)

8. **SSE ownership check**
   - Non-owner request to `/api/v1/stream/dashboard/{plant_id}` returns `403`

9. **Admin read-only endpoints**
   - `/api/v1/admin/users`: reachable for admin
   - `/api/v1/admin/sensors`: reachable for admin
   - `/api/v1/admin/alerts`: reachable for admin
   - `/api/v1/admin/logs`: reachable for admin

## Conclusion

The system is operational as a **final diploma prototype** and demonstrates end-to-end behavior from IoT telemetry ingestion to hybrid condition assessment, recommendation exposure, alerting, role-based access control, and a supervised Random Forest support model for condition classification.
