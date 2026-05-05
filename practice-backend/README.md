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

```bash
cd /Users/zhalgassovasaniya/Downloads/Practice-main
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

```bash
cd practice-backend
cp .env.example .env
```

Optional: set bootstrap admin in `.env`:

```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=AdminPass123!
```

### 4) Run database

```bash
cd /Users/zhalgassovasaniya/Downloads/Practice-main/practice-backend
docker compose up -d
```

### 5) Apply migrations

```bash
alembic upgrade head
```

### 6) (Optional) Seed demo data

```bash
python -m scripts.bootstrap_demo
```

### 7) Run application

```bash
uvicorn app.main:app --reload
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/health
```

### 8) Run tests

```bash
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
- `POST /sensors`
- `GET /sensors`
- `POST /sensors/{sensor_id}/attach`
- `POST /sensors/{sensor_id}/detach`
- `POST /sensors/{sensor_id}/rotate-token`

### US4 - Dashboard and current status
- `GET /dashboard/plants/{plant_id}?hours=24`

### US5 - Critical alert creation
- `POST /ingest/sensors/{device_id}/data`
- (alerts become visible via `GET /alerts` and SSE `/stream/alerts`)

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

### US8 - Admin monitoring
- `GET /admin/users`
- `GET /admin/sensors`
- `GET /admin/alerts`
- `GET /admin/logs`

### Real-time streams (SSE)
- `GET /stream/alerts`
- `GET /stream/dashboard/{plant_id}`

## Smoke Test Artifacts

- HTTP scenario file: `http/smoke-test.http`
- Acceptance mapping: `docs/acceptance-checklist.md`
- Demo seed script: `scripts/bootstrap_demo.py`

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
  -d '{"name":"Monstera Demo","species":"Monstera Deliciosa","location":"Living room"}'
```

### Attach sensor

Registering a sensor requires a user token and returns a one-time `device_token` for IoT ingest.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"demo-sensor-001","type":"multi"}'
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors/<SENSOR_ID>/attach \
  -H "Authorization: Bearer <USER_TOKEN>" \
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
