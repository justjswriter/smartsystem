# Diploma Work Implementation Analysis Report

**Project title:** Developing a Smart System with IoT Integration and Artificial Intelligence Technologies for Plant Condition Monitoring

**Analysis basis:** Repository code at `smartsystem` (May 2026). Active implementation paths: `practice-backend/`, `smart-plant-frontend/`, `iot/`. Legacy reference only: `diploma practice part/`.

---

## 1. Project Overview

### What was developed

A **functional web application** for **indoor environmental plant condition monitoring**. Users register, manage plant profiles, view sensor telemetry on dashboards, receive threshold-based alerts and rule-based care recommendations, and see **hybrid rule-based + Random Forest** condition classification on the dashboard. Administrators provision USB-connected sensor nodes and assign them to users and plants.

### Practical goal and problem

The system helps a plant owner **observe four environmental parameters** (soil moisture, air temperature, air humidity, light intensity) over time, detect out-of-range conditions, and get **actionable care guidance** without manual log-keeping. It addresses fragmented monitoring: raw sensor values are collected, stored, analyzed, and presented in one place.

### Why environmental monitoring and these four parameters

These four signals are directly measurable with the implemented Arduino stack (capacitive soil probe, DHT11, LDR) and are commonly used for **houseplant care decisions** (watering, humidity, temperature stress, light adequacy). They do not require vision, disease models, or actuators.

### Actual project boundaries

| Implemented | Intentionally excluded (per scope and code) |
|-------------|---------------------------------------------|
| Web dashboard, auth, plant CRUD | Plant disease diagnosis |
| USB Arduino Uno → serial gateway → REST ingest | Computer vision, deep learning |
| PostgreSQL persistence, history charts | Irrigation / actuator control |
| Threshold alerts, FSM lifecycle, in-app notifications | Greenhouse automation, WSN deployment |
| Rule-based recommendations + RF classifier support | Real-world agronomic validation |
| Admin sensor provisioning, device tokens | ESP32 direct-to-backend path (legacy only) |

### Concise technical summary

**Arduino Uno** (5 s interval, 9600 baud JSON lines) → **Python serial gateway** (normalization, HTTP POST) → **FastAPI** async API (JWT users, hashed device tokens) → **PostgreSQL** → **React + TypeScript** dashboard with **SSE** updates. Condition logic: **plant care profile thresholds** (Golden pothos / *Epipremnum aureum*), **alert deduplication**, **RandomForestClassifier** (8 features, 3 classes) as supporting signal; rule-based status remains primary when ML disagrees.

---

## 2. Repository Structure and System Components

| Module | Path | Purpose | Status | Key files |
|--------|------|---------|--------|-----------|
| Backend API | `practice-backend/` | REST API, ingest, alerts, ML, SSE | **Active** | `app/main.py`, `app/api/v1/routers/*`, `app/application/services/*` |
| Frontend dashboard | `smart-plant-frontend/` | React UI, charts, i18n | **Active** | `src/router.tsx`, `src/api.ts`, `src/context/AppStateContext.tsx`, `src/pages/*` |
| Arduino firmware | `iot/arduino_uno_sensor_node/` | Sensor sampling, serial JSON | **Active** | `arduino_uno_sensor_node.ino`, `SoilMoisture.*`, `DHT.*`, `LDR.*` |
| Python gateway | `iot/serial_gateway/` | Serial read, normalize, POST ingest | **Active** | `serial_gateway.py`, `README.md`, `tests/test_serial_gateway.py` |
| ORM models | `practice-backend/app/infrastructure/models/` | SQLAlchemy entities | **Active** | `models.py`, `base.py` |
| Migrations | `practice-backend/alembic/versions/` | Schema evolution | **Active** | `0001`–`0009` revisions |
| AI/ML | `practice-backend/app/ml/` | Train RF, dataset, inference | **Active** | `train_condition_model.py`, `plant_condition_model.joblib`, `model_metadata.json` |
| Domain knowledge | `practice-backend/app/domain/plant_knowledge/` | Thresholds, issues, advice | **Active** | `profiles.py`, `types.py` |
| Config / infra | `practice-backend/app/core/`, `docker-compose.yml` | Settings, DB, security | **Active** | `config.py`, `database.py`, `security.py` |
| Backend tests | `practice-backend/tests/` | pytest unit/integration-style | **Active** | 10 test modules |
| Gateway tests | `iot/serial_gateway/tests/` | Normalization unit tests | **Active** | `test_serial_gateway.py` |
| Documentation | `practice-backend/README.md`, `docs/`, `docs/ai-module.md` | Setup, acceptance, AI notes | **Active** | `acceptance-checklist.md`, `demo-runbook.md` |
| Demo scripts | `practice-backend/scripts/` | Seed, simulate ingest | **Active** | `bootstrap_demo.py`, `simulate_sensor_data.py` |
| LaTeX thesis draft | `diploma-latex/` | Written thesis structure | **Supporting** | `chapters/*.tex` |
| Legacy prototype | `diploma practice part/` | Older ESP32 + Supabase stack | **Legacy** | `README.md` marks archived |

### Component interaction

```text
[Arduino Uno] --USB serial JSON--> [serial_gateway.py] --HTTPS POST + X-Device-Token-->
[FastAPI ingest] --> [PostgreSQL] <-- [React frontend via REST + SSE]
                              --> [AlertService: thresholds, alerts, recommendations, notifications]
                              --> [MonitoringService: dashboard + PlantConditionService + ML]
```

The frontend does not talk to the Arduino directly. Only one process may hold the COM port (gateway or Serial Monitor).

---

## 3. System Architecture

### Client–server structure

- **Client:** SPA (`smart-plant-frontend`, Vite + React 19 + TypeScript).
- **Server:** `practice-backend` (FastAPI, layered: API → application services → domain → infrastructure).
- **IoT edge:** Arduino + separate Python process (not embedded in backend).

### Data flow (step-by-step)

1. **Arduino** reads soil raw (A1), DHT11 humidity/temperature (pin 2), LDR raw (A3); every **5000 ms** prints one JSON line at **9600 baud**.
2. **Serial gateway** reads lines, parses JSON, **normalizes** to backend units (`moisture` %, `humidity`/`temperature`, `light` 0–1000 scale), rate-limits sends (default **5 s**).
3. **POST** `/api/v1/ingest/sensors/{device_id}/data` with headers `X-Device-Token`, `X-Ingest-Source` (e.g. `serial:COM3`).
4. **Validation:** device exists, token verified (bcrypt hash), sensor active, attached to a plant; Pydantic `SensorDataIngest` schema.
5. **Storage:** row in `sensor_data`; sensor `last_seen_at`, `status=online`, `last_ingest_source` updated.
6. **Threshold analysis:** `AlertService._evaluate_thresholds` against `resolve_plant_profile(species)` issue definitions; dedupe window **5 minutes**; special sustained high-moisture logic; night window suppresses low-light alerts (local offset UTC+5, 20:00–07:00).
7. **Alerts / recommendations / notifications:** new `alerts`, `recommendations`, `notifications`; SSE publish to `alerts:{user_id}`, `notifications:{user_id}`, `dashboard:{plant_id}`.
8. **Dashboard:** user calls `GET /dashboard/plants/{id}` or receives SSE `sensor_data` on plant detail page; charts from `history`; `PlantConditionService` + optional ML enrichment.

### Technology choices (as evidenced in repo)

| Choice | Evidence / role |
|--------|-----------------|
| **FastAPI** | `app/main.py`, async routes, OpenAPI at `/docs`, Pydantic v2 schemas |
| **PostgreSQL** | `docker-compose.yml` postgres:17, `asyncpg`, Alembic migrations |
| **React + TypeScript** | `smart-plant-frontend/package.json`, typed `api.ts`, `types.ts` |
| **Python gateway** | `iot/serial_gateway/README.md`: Uno has no Wi-Fi/API credentials; gateway holds token, normalization, retries |
| **Async backend** | `AsyncSession`, `asyncpg`, async route handlers |
| **REST** | `/api/v1/*` resource routers |
| **SSE** | `sse-starlette`, `stream.py`, frontend `@microsoft/fetch-event-source` |

### Asynchronous communication

- **HTTP REST** for CRUD, dashboard, alerts, notifications.
- **SSE** (`GET /stream/alerts`, `/stream/notifications`, `/stream/dashboard/{plant_id}`) with in-memory `EventBus` (not Redis); heartbeat every `SSE_HEARTBEAT_SECONDS` (default 15).

### Evidence files

- Architecture narrative: `practice-backend/README.md`, `iot/serial_gateway/README.md`
- Ingest pipeline: `app/application/services/alert_service.py`, `app/api/v1/routers/ingest.py`
- Streams: `app/api/v1/routers/stream.py`, `app/infrastructure/services/event_bus.py`
- Frontend SSE: `AppStateContext.tsx`, `PlantDetailsPage.tsx`

---

## 4. Backend Implementation

### Authentication and authorization

- **JWT:** `python-jose`, `create_access_token` / `decode_access_token`, Bearer scheme in `app/api/deps.py`.
- **Password hashing:** `bcrypt` via `hash_password` / `verify_password` in `app/core/security.py`.
- **Roles:** `UserRole` enum `user` \| `admin`; `require_admin` dependency for sensor provisioning and admin routes.
- **Protected endpoints:** `get_current_user` requires valid JWT and **`users.is_active = true`**.
- **Inactive users:** `AuthService.login` does not explicitly check `is_active`, but subsequent API calls fail authentication once inactive.
- **Device auth:** ingest uses `X-Device-Token`; only **bcrypt hash** stored in `sensors.device_token_hash`; plaintext shown once on create/rotate.
- **Bootstrap admin:** optional `ADMIN_EMAIL` / `ADMIN_PASSWORD` in lifespan (`app/main.py`).

**Key files:** `auth.py` router, `auth_service.py`, `security.py`, `deps.py`.

### Plant management

- CRUD under `/api/v1/plants`; soft delete via `is_active` / `deleted_at`.
- **Ownership:** `plants.user_id` FK; repositories filter by user unless admin.
- **Species** links to care profile resolution (`resolve_plant_profile`).
- **Care profiles API:** `plant_care_profiles` router; DB table `plant_care_profiles` (seeded Golden pothos).

**Key files:** `plants.py` router, `plant_service.py`, `plant_repository.py`.

### Sensor management

- **Admin-only:** create sensor (`device_id`, `type`), assign to `user_id`, attach/detach `plant_id`, rotate token.
- **Users:** read-only list of assigned or plant-attached sensors.
- **Types:** enum `soil_moisture`, `temperature`, `air_humidity`, `light`, `multi` (default multi).
- **Status:** `offline` \| `online` \| `disabled`; online after successful ingest.

**Key files:** `sensors.py` router, `sensor_service.py`, migration `0002_iot_condition_fields.py`.

### Data ingestion

- Endpoint: `POST /api/v1/ingest/sensors/{device_id}/data`.
- Body (`SensorDataIngest`): optional `moisture`, `temperature`, `humidity`, `light`, `recorded_at`.
- Flow in `AlertService.ingest_sensor_data`: auth → disabled check → plant attachment → `SensorDataRepository.create` → threshold evaluation → SSE dashboard event.
- Errors: 401 invalid token, 400 validation/disabled/not attached; `system_logs` for auth failures.

### Monitoring logic

- `MonitoringService.get_dashboard`: latest point + history for `hours` (1–720), `PlantConditionService.evaluate`, `RecommendationService.build_current_recommendation`, optional DB care profile payload.
- Charts/history: time-series from `sensor_data` indexed by `plant_id`, `recorded_at`.

### Alerts and recommendations

- **Alerts:** metric/direction vs profile `issues`; severity from deviation ratio; FSM transitions via `alert_workflow_service` / `alerts` router.
- **Recommendations:** `RecommendationService.create_for_alert` on alert; dashboard “current” recommendation from live readings or stable advice.
- **Notifications:** persisted, dedupe by `dedupe_key`; optional **SMTP** email (`EMAIL_NOTIFICATIONS_ENABLED`, `email_service.py`) — off by default.

**Backend service map:** `AuthService`, `PlantService`, `SensorService`, `AlertService`, `MonitoringService`, `PlantConditionService`, `MLConditionService`, `RecommendationService`, `NotificationService`, `NotificationSettingsService`, admin/monitoring routers.

---

## 5. Database Design

### Database overview — tables

| Table | Purpose |
|-------|---------|
| `users` | Accounts, role, password hash, avatar, `is_active` |
| `plants` | User-owned plant profiles |
| `plant_care_profiles` | Species thresholds, care JSON (kk/ru/en content) |
| `sensors` | Device registry, token hash, plant assignment, ingest metadata |
| `sensor_data` | Telemetry time series |
| `alerts` | Threshold violations, severity, metric snapshot |
| `alert_transitions` | FSM audit trail |
| `recommendations` | Care text linked to plant/alert |
| `notifications` | In-app notification feed |
| `user_notification_settings` | Email preferences per user |
| `system_logs` | Audit/events (register, login, ingest failures, alerts) |

### Important relationships

- `users` 1—\* `plants`, `alerts`, `notifications`
- `plants` 1—\* `sensors` (optional FK), `sensor_data`, `alerts`, `recommendations`
- `sensors` 1—\* `sensor_data`; optional `user_id` assignment
- `alerts` \*—\* `recommendations`, `notifications`; `alert_transitions` child

### Integrity and enums

- PostgreSQL enums: `user_role`, `sensor_type`, `sensor_status`, `alert_status`, `alert_severity`, `notification_type`, `notification_severity`, transition enums.
- Unique: `users.email`, `sensors.device_id`, `plant_care_profiles.slug` / `canonical_species`.
- Timestamps: `created_at` / `updated_at` on main entities; `sensor_data.recorded_at` for telemetry time.

### Simplified ERD (relationship list)

```text
users ──< plants ──< sensor_data
  │        │
  │        ├──< sensors (plant_id nullable)
  │        ├──< alerts ──< alert_transitions
  │        ├──< recommendations
  │        └──< notifications
users ──< alerts
users ──o user_notification_settings
plant_care_profiles (standalone reference data)
sensors ──< sensor_data
```

### Persistent vs computed

| Persistent | Computed at request time |
|------------|---------------------------|
| `sensor_data` rows | `health_score`, `condition_status`, ML prediction |
| `alerts`, `recommendations`, `notifications` | Dashboard `active_recommendation` from current readings |
| User/plant/sensor registry | Trend features for ML (last − first in history window) |
| Care profiles in DB + code profiles | Severity ratio for new alerts |

**Migrations:** `0001_init_mvp_schema` through `0009_user_avatar_url` (notifications, care profiles, seeds, avatar).

---

## 6. IoT Integration

### Arduino node

| Parameter | Implementation |
|-----------|----------------|
| Board | Arduino Uno (`README`: Board: Arduino Uno) |
| Soil moisture | Capacitive sensor, analog A1, `SoilMoisture` class → `soil_raw` |
| Air humidity / temperature | DHT11, data pin 2 |
| Light | LDR analog A3 → `light_raw` |
| Interval | `READ_INTERVAL_MS = 5000` |
| Baud rate | `SERIAL_BAUD_RATE = 9600` |
| Format | Single-line JSON per reading |

**Sample Arduino serial line:**

```json
{"soil_raw":40,"humidity":36.5,"temperature":27.1,"light_raw":120}
```

**With failed DHT reads:**

```json
{"soil_raw":220,"humidity":null,"temperature":null,"light_raw":5}
```

### Python gateway

- Reads UTF-8 lines, extracts JSON object, validates numeric fields.
- **Normalization** (`normalize_reading`):
  - `moisture` = linear map from `soil_raw` using wet/dry calibration (defaults 0 / 220).
  - `light` = `light_raw / 1023 * 1000`.
  - `humidity` += default offset **20** (configurable; documents DHT under-read).
- POST with retries on serial/HTTP errors (`--retry-delay` default 5 s).
- **Not wireless:** USB serial only; no ESP8266/ESP32 in active path.

**Normalized payload example** (from gateway tests, default calibration):

```json
{
  "moisture": 100.0,
  "humidity": 56.5,
  "temperature": 27.1,
  "light": 117.3
}
```

**Backend ingest example** (from README):

```json
{"moisture":18.0,"temperature":37.2,"humidity":24.5,"light":160.0}
```

**Evidence:** `iot/arduino_uno_sensor_node/arduino_uno_sensor_node.ino`, `iot/serial_gateway/serial_gateway.py`, `iot/serial_gateway/README.md`.

---

## 7. AI/ML Module

### Implementation

- **Algorithm:** `RandomForestClassifier` (scikit-learn), `n_estimators=240`, `max_depth=12`, `class_weight="balanced_subsample"`.
- **Training script:** `app/ml/train_condition_model.py`; artifact `plant_condition_model.joblib`; metadata `model_metadata.json`.
- **Dataset:** synthetic CSV `training_dataset.csv` — **420 rows** (140 per class), generated from Golden pothos threshold ranges in `resolve_plant_profile()`.
- **Labels:** `normal`, `attention`, `critical`.
- **Features (8):** `moisture`, `temperature`, `humidity`, `light`, `moisture_trend`, `temperature_trend`, `humidity_trend`, `light_trend` (trends from dashboard history delta).
- **Inference:** `MLConditionService.predict_condition`; `predict_proba` → `ml_confidence`, `class_probabilities`.
- **Fallback:** if model file missing or load fails → `analysis_method: "rule_based"`, ML fields null; ingest/alerts unaffected.

### Hybrid with rules

- `PlantConditionService` computes rule-based `condition_status` (`normal` \| `attention` \| `critical`), `health_score` (0–100), penalties from profile issues + trend penalty.
- ML is **supporting**; if prediction differs, explanation states **rule-based status remains primary for safety** (`_merge_explanations`).
- Metadata records **accuracy: 1.0** on held-out synthetic test split — reflects synthetic separability, not field validation.

### Limitations (explicit in code/docs)

- No disease diagnosis, vision, or external AI APIs (`docs/ai-module.md`).
- Training data is **expert-labeled synthetic**, not biological ground truth.
- Single dominant care profile in production logic (Golden pothos / aroid seed).

---

## 8. Frontend and Dashboard

### Stack and structure

- **React 19 + TypeScript + Vite 8**; routing via `react-router-dom`.
- **Charts:** Recharts (`Analytics.tsx`, plant detail).
- **i18n:** Kazakh default, Russian and English (`i18n.tsx`).
- **State:** `AppStateContext` — JWT in `localStorage`, plants/alerts/sensors/notifications, admin sensor APIs.

### Pages and routes

| Route | Page | Role |
|-------|------|------|
| `/login`, `/register` | Auth | Public |
| `/` | Dashboard | Protected |
| `/plants`, `/plants/:id` | Plant list / detail + live SSE | User |
| `/analytics` | Historical analytics | User |
| `/sensors` | Read-only sensor status | User |
| `/alerts` | Alert list + FSM actions | User |
| `/admin` | User/sensor provisioning | Admin |
| `/profile` | Profile, password, avatar, weather city preference | User |

### User interaction

1. Register/login → Bearer token on API calls.
2. Create plant (species for care profile).
3. Admin creates sensor, copies **one-time** device token, assigns user, attaches plant.
4. Run gateway or simulation script → dashboard updates (polling + SSE on plant page).
5. View condition card (score, explanation, ML fields if available), charts, recommendations, alerts; mark notifications read.

### Near real-time

- SSE: alerts and notifications globally; per-plant dashboard stream on `PlantDetailsPage`.
- Polling/refetch also used in context loaders.

### UX notes (non-sensor)

- **Weather banner** on dashboard uses public **Open-Meteo** API and user-selected city from profile (`weatherCities.ts`) — decorative context, not plant telemetry.

**Major components:** `Dashboard.tsx`, `PlantDetails.tsx`, `Analytics.tsx`, `Alerts.tsx`, `NotificationsPanel.tsx`, `Sensors.tsx`, `AdminPage.tsx`, `ProtectedLayout.tsx`.

---

## 9. Technical Challenges and Engineering Decisions

| Decision | Rationale (code-evidenced) |
|----------|----------------------------|
| Split gateway from firmware | Arduino has no network stack or secrets; gateway handles token, HTTP, calibration |
| USB not Wi-Fi | Uno limitations; documented single COM port exclusivity |
| Hashed device tokens | `hash_device_token` uses bcrypt; plaintext never stored |
| Admin-only sensor lifecycle | Prevents users from spoofing arbitrary `device_id` ingest |
| Plant care profile in code + DB | Threshold-driven alerts/recommendations; seeded migrations `0006`–`0008` |
| Alert dedupe 5 min | Avoid spam on noisy readings (`AlertService.DEDUPE_WINDOW`) |
| Night suppression for low light | Avoid false “needs light” alerts at night (UTC+5 local heuristic) |
| Sustained high moisture | Requires history before alerting (`_is_sustained_high_moisture`) |
| In-memory EventBus | Simple SSE for prototype; not horizontally scalable |
| ML does not drive actuators | Rule-primary merge when ML disagrees |
| Layered backend | README documents API / application / domain / infrastructure separation |
| Legacy folder retained | `diploma practice part/README.md` states archived ESP32/Supabase prototype |

**Sensor calibration challenge:** gateway documents DHT under-read (`--humidity-offset` 20) and soil wet/dry raw range; warnings when raw values outside calibrated range.

---

## 10. Testing and Validation

### What exists

| Area | Coverage |
|------|----------|
| Backend unit tests | `practice-backend/tests/` — security (JWT, bcrypt, device token), plant condition scoring, ML service, alert FSM, dedup, notifications, sensor lifecycle, plant knowledge, notification settings |
| Gateway unit tests | `iot/serial_gateway/tests/test_serial_gateway.py` — normalization, URL builder, JSON parse |
| Manual API | `http/smoke-test.http`, Swagger `/docs` |
| Demo validation | `docs/acceptance-checklist.md`, `scripts/bootstrap_demo.py`, `simulate_sensor_data.py`, `run_full_demo_flow.py` |
| Build | Frontend `npm run build` (tsc + vite); backend run via uvicorn |

### What is not evidenced

- No dedicated frontend automated test suite in repo.
- No end-to-end Playwright/Cypress suite.
- Gateway tests do not hit live serial/hardware in CI by default.
- ML accuracy on synthetic data should not be reported as ecological validation.

### Reliability checks

- Docker Postgres healthcheck; pytest for core business rules; ingest error logging to `system_logs`.

---

## 11. Practical Results of the Project

### Achieved

- End-to-end **software prototype**: register users, manage plants, provision sensors, ingest real or simulated telemetry, store history, visualize charts, classify condition (rules + RF), generate alerts and recommendations, notify users (in-app + optional email), admin oversight, tri-lingual UI.
- **Physical path demonstrated:** Arduino Uno + USB gateway documented and integrated with existing ingest API.
- **Decision support:** explainable health score, risk factors, confidence, ML probabilities when model present.

### Not achieved (by design)

- Disease detection, CV, DL, actuators, farm-scale automation, wireless mesh, agronomic field studies.

---

## 12. Recommended Evidence for Report

| # | Title | Demonstrates | Source |
|---|--------|--------------|--------|
| 1 | System architecture diagram | Full data path Uno → gateway → API → DB → UI | Draw from `practice-backend/README.md`, `iot/serial_gateway/README.md` |
| 2 | ERD diagram | Tables and FKs | `models.py`, `0001_init_mvp_schema.py` |
| 3 | Arduino Serial Monitor capture | Raw JSON lines, 5 s interval | `arduino_uno_sensor_node.ino` |
| 4 | Gateway console log | Normalized POST accepted | Run `serial_gateway.py` per `README.md` |
| 5 | Swagger `/docs` | REST surface | `uvicorn app.main:app` |
| 6 | Ingest request example | Device token auth | `README.md` cURL, `ingest.py` |
| 7 | Dashboard screenshot | Four metrics + condition card | `DashboardPage.tsx`, `GET /dashboard/plants/{id}` |
| 8 | Historical chart screenshot | Time-series analytics | `AnalyticsPage.tsx` |
| 9 | Alerts page screenshot | FSM states, severities | `AlertsPage.tsx`, `alerts` table |
| 10 | Notifications panel | Deduped in-app feed | `NotificationsPanel.tsx` |
| 11 | Admin sensor provisioning | One-time token, assign, attach | `AdminPage.tsx`, `sensors` router |
| 12 | PostgreSQL table view | `sensor_data`, `alerts` rows | Docker DB port 5444 |
| 13 | ML metadata / dashboard ML fields | RF classes and confidence | `model_metadata.json`, dashboard `condition` schema |
| 14 | pytest output | Automated validation | `pytest -q` in `practice-backend` |
| 15 | Gateway unit test output | Normalization correctness | `test_serial_gateway.py` |

---

## 13. Final Safe Technical Summary

During the diploma project implementation period, a **web-based environmental monitoring application** was developed for indoor plants. The system collects **soil moisture, air temperature, air humidity, and light intensity** using an **Arduino Uno sensor node** connected by **USB serial** to a **Python gateway**, which forwards normalized readings to a **FastAPI** backend. Data are stored in **PostgreSQL** and presented through a **React and TypeScript** dashboard with authentication, plant profiles, historical charts, alerts, in-app notifications, and **rule-based care recommendations**.

Condition assessment uses a **hybrid approach**: an explainable **rule-based** engine grounded in a **Golden pothos care profile** remains the primary safety baseline, while a **supervised Random Forest classifier** (scikit-learn) provides **AI-supported classification** into normal, attention, and critical states when the trained model is available. The ML component is trained on a **synthetic labeled dataset** for technical demonstration and is not intended for plant disease diagnosis or agronomic certification.

The implemented prototype **does not** include computer vision, deep learning, irrigation control, wireless sensor networks, or industrial automation. It demonstrates a complete **software integration chain** from USB-connected sensing to persisted analytics and user-facing decision support suitable for a diploma **functional prototype** report.

---

*Report generated from repository analysis only; no features were invented beyond verified code and documentation.*
