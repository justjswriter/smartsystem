# Practice Backend (Final Diploma Prototype)

Backend for plant monitoring built with FastAPI, async SQLAlchemy, Alembic, and PostgreSQL.

## Architecture Overview

- **API layer**: FastAPI routers and request handlers in `app/api/v1/routers`.
- **Application layer**: use-case services in `app/application/services`.
- **Domain layer**: enums and business workflow contracts in `app/domain`.
- **Infrastructure layer**: ORM models, repositories, and event bus in `app/infrastructure`.
- **Cross-cutting**: configuration, security, middleware, logging in `app/core`.

## Project Structure

```text
practice-backend/
  app/
    api/
      deps.py
      v1/routers/
        auth.py
        plants.py
        sensors.py
        monitoring.py
        ingest.py
        alerts.py
        notifications.py
        admin.py
        stream.py
    application/
      schemas/
      services/
    domain/
      enums/
    infrastructure/
      models/
      repositories/
      services/event_bus.py
    core/
      config.py
      database.py
      security.py
      middleware.py
      logging.py
    main.py
  alembic/
  scripts/
  tests/
  docker-compose.yml
  alembic.ini
```

## Setup

### 1) Create and activate virtual environment

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\practice-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

Dependencies are stored in the repository root `requirements.txt`.

```powershell
.\.venv\Scripts\python -m pip install -r ..\requirements.txt
```

### 3) Configure environment

```powershell
Copy-Item .env.example .env
```

Optional: set bootstrap admin in `.env`:

```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=AdminPass123!
```

### 4) Run database

```powershell
docker compose up -d
```

### 5) Apply migrations

```powershell
alembic upgrade head
```

### 6) (Optional) Seed demo data

```powershell
python -m scripts.bootstrap_demo
```

### 7) Run application

```powershell
uvicorn app.main:app --reload
```

Healthcheck:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 8) Run tests

```powershell
$env:PYTHONPATH='.'
pytest -q
```

### Troubleshooting

- `Cannot connect to the Docker daemon ...`: Docker Desktop is not running. Start it, then run `docker compose up -d` again.
- `Connect call failed ('127.0.0.1', 5444)`: PostgreSQL container is not up yet. Check `docker compose ps` and retry migrations.
- `ModuleNotFoundError: No module named 'app'` while seeding: run from `practice-backend` and use `python -m scripts.bootstrap_demo`.
- `DuplicateObjectError: type "user_role" already exists`: schema is in mixed state; run `docker compose down -v && docker compose up -d` and then `alembic upgrade head`.

## API Endpoints Grouped by User Stories

Base prefix: `/api/v1`

### US1 - Registration and login
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### US2 - Plant profile management
- `POST /plants`
- `GET /plants`
- `GET /plants/{plant_id}`
- `PATCH /plants/{plant_id}`
- `DELETE /plants/{plant_id}`

### US3 - Sensor onboarding and binding
- `POST /sensors` (admin-only, returns one-time `device_token`)
- `GET /sensors` (admin sees all; user sees only assigned or attached-to-own-plant sensors)
- `POST /sensors/{sensor_id}/assign` (admin-only)
- `POST /sensors/{sensor_id}/attach` (admin-only)
- `POST /sensors/{sensor_id}/detach` (admin-only)
- `POST /sensors/{sensor_id}/rotate-token` (admin-only, returns one-time `device_token`)

Sensors are rental/provisioned assets. Regular users do not create, attach, detach, or rotate sensor tokens. Users can only view assigned sensors, online/offline status, attached plant, `last_seen_at`, source, and readings.

### US4 - Dashboard and current status
- `GET /dashboard/plants/{plant_id}?hours=24`

### US5 - Critical alert creation
- `POST /ingest/sensors/{device_id}/data`
- Alerts become visible via `GET /alerts` and SSE `/stream/alerts`.
- New alerts create persisted in-app notifications, visible via `GET /notifications` and SSE `/stream/notifications`.

### US6 - Care recommendations (rule-based)
- Recommendation creation is triggered inside ingest/alert pipeline.
- Dashboard returns explainable plant condition scoring and active recommendation.
- User-facing alert visibility:
  - `GET /alerts`
  - `GET /alerts/{alert_id}`

### US7 - Alert lifecycle and FSM
- `GET /alerts`
- `GET /alerts/{alert_id}`
- `POST /alerts/{alert_id}/transition`

Allowed transitions:
- `created -> viewed|acknowledged|resolved`
- `viewed -> acknowledged|resolved`
- `acknowledged -> resolved`
- `resolved -> closed`

### US7A - In-app notifications
- `GET /notifications?unread_only=false&limit=20&offset=0`
- `POST /notifications/{notification_id}/read`
- `POST /notifications/read-all`

Notifications are scoped to the current user. They are created from newly created alerts and deduplicated by `dedupe_key`, so repeated readings do not create notification spam while the alert is already open.

### US8 - Admin monitoring
- `GET /admin/users`
- `GET /admin/sensors`
- `GET /admin/alerts`
- `GET /admin/logs`

### Real-time streams (SSE)
- `GET /stream/alerts`
- `GET /stream/dashboard/{plant_id}`
- `GET /stream/notifications`

## Frontend and i18n

The React frontend is Kazakh-first by default, with Russian and English language options. Current plant condition labels, recommendations, alerts, notifications, sensor views, and admin provisioning controls are localized in `kk`, `ru`, and `en`.

## Plant Knowledge Base

The current implemented plant profile is Golden pothos / Epipremnum aureum. Condition thresholds and recommendations use the local plant knowledge base for this plant profile.

## Smoke Test Artifacts

- HTTP scenario file: `http/smoke-test.http`
- Acceptance mapping: `docs/acceptance-checklist.md`
- Demo seed script: `scripts/bootstrap_demo.py`

## Arduino Uno USB Serial Gateway

The real Arduino Uno integration path uses the existing ingest endpoint and does not require a new backend route:

```text
Arduino Uno -> USB Serial COM port -> Python Serial Gateway -> FastAPI -> PostgreSQL -> frontend dashboard
```

Provision a sensor as admin, copy its one-time device token, assign it to a user, attach it to that user's plant, then run the gateway from `../iot/serial_gateway`.

Endpoint used by the gateway:

```http
POST /api/v1/ingest/sensors/{device_id}/data
X-Device-Token: <device_token>
X-Ingest-Source: serial:COM3
```

Gateway setup and Arduino upload instructions are in `../iot/serial_gateway/README.md`.

Quick verification checklist:

- `GET /health` returns `{"status":"ok"}`.
- Admin page provisions the Arduino sensor; the user's Sensors page shows it read-only as `online`.
- Sensor `last_seen_at` updates after gateway ingest.
- Sensor `last_ingest_source` shows the gateway source label, for example `serial:COM3`.
- Plant dashboard shows current moisture, temperature, humidity, and light score.
- Critical readings still create alerts and recommendations.

## cURL Examples (Main Flows)

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name":"Demo User",
    "email":"demo@example.com",
    "password":"DemoPass123!",
    "password_confirm":"DemoPass123!"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"DemoPass123!"}'
```

### Create plant

```bash
curl -X POST http://127.0.0.1:8000/api/v1/plants \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Golden Pothos Demo","species":"Epipremnum aureum","location":"Living room"}'
```

### Admin provision and attach sensor

Creating a sensor requires an admin token and returns a one-time `device_token` for IoT ingest.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"demo-sensor-001","type":"multi"}'
```

Assign the sensor to the user who owns the plant:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors/<SENSOR_ID>/assign \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"user_id":<USER_ID>}'
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors/<SENSOR_ID>/attach \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"plant_id":<PLANT_ID>}'
```

### Send sensor data (ingest)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ingest/sensors/demo-sensor-001/data \
  -H "X-Device-Token: <DEVICE_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"moisture":18.0,"temperature":37.2,"humidity":24.5,"light":160.0}'
```

### Open dashboard

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/dashboard/plants/<PLANT_ID>?hours=24" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### Alert transition (FSM)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/alerts/<ALERT_ID>/transition \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"to_status":"viewed","note":"Seen in dashboard"}'
```

### Notifications

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/notifications?unread_only=false&limit=20&offset=0" \
  -H "Authorization: Bearer <USER_TOKEN>"
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/notifications/<NOTIFICATION_ID>/read \
  -H "Authorization: Bearer <USER_TOKEN>"
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/notifications/read-all \
  -H "Authorization: Bearer <USER_TOKEN>"
```

### Admin endpoint

```bash
curl -X GET http://127.0.0.1:8000/api/v1/admin/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### SSE streams

```bash
curl -N -H "Authorization: Bearer <USER_TOKEN>" \
  http://127.0.0.1:8000/api/v1/stream/alerts
```

```bash
curl -N -H "Authorization: Bearer <USER_TOKEN>" \
  http://127.0.0.1:8000/api/v1/stream/dashboard/<PLANT_ID>
```

```bash
curl -N -H "Authorization: Bearer <USER_TOKEN>" \
  http://127.0.0.1:8000/api/v1/stream/notifications
```
