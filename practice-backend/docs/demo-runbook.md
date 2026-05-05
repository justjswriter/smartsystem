# Live Demo Runbook (5-7 minutes)

This runbook is optimized for a short live demo of all 8 user stories without changing code.

## Demo Goal

Show full flow: onboarding -> monitoring -> alert handling -> admin monitoring.

## Demo Data

Use seeded credentials and entities from `scripts/bootstrap_demo.py`:

- Demo user: `demo@example.com` / `DemoPass123!`
- Admin user: `admin@example.com` / `AdminPass123!`
- Demo sensor device id: `demo-sensor-001`
- Demo sensor token: `DemoDeviceToken123!`

## 0) Pre-demo setup (1-2 minutes)

Run these commands from project root:

```bash
cd /Users/zhalgassovasaniya/Downloads/Practice-main
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd practice-backend
cp .env.example .env
docker compose up -d
alembic upgrade head
python -m scripts.bootstrap_demo
uvicorn app.main:app --reload
```

If `docker compose up -d` fails with `Cannot connect to the Docker daemon`, start Docker Desktop first and retry.

Quick health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected result: `{"status":"ok","service":"Practice Backend"}`.

## 1) US1 Registration/Login (40-60 sec)

### Register a fresh user (optional if already exists)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Live Demo User","email":"live-demo@example.com","password":"LivePass123!","password_confirm":"LivePass123!"}'
```

Expected result: user object with `id`, `email`, `role=user`.

### Login demo user

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"DemoPass123!"}'
```

Copy `access_token` as `USER_TOKEN`.

Expected result: `access_token` + user payload.

## 2) US2 Plant profile (40-60 sec)

Create plant:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/plants \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Plant 2","species":"Ficus","location":"Kitchen"}'
```

Expected result: plant created with `id`.

List plants:

```bash
curl -X GET http://127.0.0.1:8000/api/v1/plants \
  -H "Authorization: Bearer USER_TOKEN"
```

Expected result: list contains seeded `Demo Monstera` and new plant.

## 3) US3 Sensor attach (30-40 sec)

Register sensor (if needed):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"live-sensor-001","type":"soil_moisture"}'
```

Copy the returned `device_token`; it is shown only once and must be used by the IoT device as `X-Device-Token`.

Attach sensor to chosen plant:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sensors/SENSOR_ID/attach \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plant_id":PLANT_ID}'
```

Expected result: sensor `plant_id` is set, status becomes `online`.

## 4) US4 + US5 + US6 Monitoring, alerts, recommendations (1-2 min)

Send critical telemetry:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ingest/sensors/demo-sensor-001/data \
  -H "X-Device-Token: DemoDeviceToken123!" \
  -H "Content-Type: application/json" \
  -d '{"moisture":12.0,"temperature":39.0,"humidity":20.0,"light":120.0}'
```

Expected result: `{"status":"accepted","sensor_data_id":...}` and alert generation.

Open dashboard:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/dashboard/plants/PLANT_ID?hours=24" \
  -H "Authorization: Bearer USER_TOKEN"
```

Expected result: `current`, `history`, `condition.health_score`, `condition.condition_status`, and active recommendation when risk exists.

Check alerts:

```bash
curl -X GET http://127.0.0.1:8000/api/v1/alerts \
  -H "Authorization: Bearer USER_TOKEN"
```

Expected result: new alert(s) with severity/metric and a user-visible recommendation.

## 5) US7 Alert FSM transitions (45-60 sec)

Perform transitions on `ALERT_ID`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/alerts/ALERT_ID/transition \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to_status":"viewed","note":"demo"}'
```

Then repeat with:
- `acknowledged`
- `resolved`
- `closed`

Expected result: each step returns transition object; invalid transitions are rejected.

## 6) US8 Admin monitoring (40-60 sec)

Login admin:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPass123!"}'
```

Copy token as `ADMIN_TOKEN`, then call:

```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" http://127.0.0.1:8000/api/v1/admin/users
curl -H "Authorization: Bearer ADMIN_TOKEN" http://127.0.0.1:8000/api/v1/admin/sensors
curl -H "Authorization: Bearer ADMIN_TOKEN" http://127.0.0.1:8000/api/v1/admin/alerts
curl -H "Authorization: Bearer ADMIN_TOKEN" http://127.0.0.1:8000/api/v1/admin/logs
```

Expected result: admin can view users/devices/alerts/logs.

## 7) SSE real-time view (optional 30 sec)

Open stream in separate terminal:

```bash
curl -N -H "Authorization: Bearer USER_TOKEN" http://127.0.0.1:8000/api/v1/stream/alerts
```

And dashboard stream:

```bash
curl -N -H "Authorization: Bearer USER_TOKEN" http://127.0.0.1:8000/api/v1/stream/dashboard/PLANT_ID
```

Expected result: heartbeat events and new events after ingest/transition actions.
