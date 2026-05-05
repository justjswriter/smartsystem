# Plant monitoring — FastAPI backend

Main setup (Supabase, Uvicorn, Alembic, frontend) is in the root [README.md](../README.md). This file only adds quick **curl** examples.

## Quick reference

- `cp .env.example .env` and set `DATABASE_URL` to your team **Supabase** connection string, plus `SECRET_KEY` and `DEVICE_API_KEY`
- `alembic upgrade head` (creates tables: `users`, `plants`, `sensors`, `sensor_readings`, `alerts`, `recommendations` in the remote database)
- `uvicorn app.main:app --reload --port 8001`

`DATABASE_URL` is loaded with **pydantic-settings** from `.env` in this folder. **Alembic** uses the same value via `alembic/env.py`.

### Team `DATABASE_URL`

One shared **Supabase** (or any PostgreSQL) database URL. Every clone of the repo uses the same `DATABASE_URL` in local `.env` (never commit real credentials).

### Example: register and ingest (curl)

```bash
# Register
curl -s -X POST "http://127.0.0.1:8001/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo","email":"demo@example.com","password":"secretword1"}'

# Login (use access_token in Authorization for protected routes)
curl -s -X POST "http://127.0.0.1:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secretword1"}'

# Ingest (use DEVICE_API_KEY from .env, no JWT)
curl -s -X POST "http://127.0.0.1:8001/api/readings/ingest" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_DEVICE_API_KEY" \
  -d '{
    "device_id": "esp32-plant-001",
    "plant_id": 1,
    "soil_moisture_raw": 500,
    "temperature": 26,
    "humidity": 40,
    "light_raw": 700
  }'
```

Replace `PLANT_ID` and the device key with your real values.
