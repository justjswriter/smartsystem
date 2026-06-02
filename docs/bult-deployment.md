# Bult.ai Deployment

Use this when deploying from GitHub to Bult.ai.

## Services

Create three services:

1. PostgreSQL database from Bult PostgreSQL template.
2. Backend from GitHub using Dockerfile.
3. Frontend from GitHub using Dockerfile.

## Backend Service

Git source:

```text
Repository: your GitHub repository
Context: .
Dockerfile: practice-backend/Dockerfile
```

Environment variables:

```env
APP_NAME=Practice Backend
APP_ENV=production
APP_DEBUG=false
API_V1_PREFIX=/api/v1

POSTGRES_HOST=<bult_postgres_host>
POSTGRES_PORT=5432
POSTGRES_DB=<bult_postgres_database>
POSTGRES_USER=<bult_postgres_user>
POSTGRES_PASSWORD=<bult_postgres_password>
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>

SECRET_KEY=<long_random_secret>
ACCESS_TOKEN_EXPIRE_MINUTES=120
ALGORITHM=HS256

CORS_ORIGINS=["https://<frontend-public-url>"]

LOG_LEVEL=INFO

MOISTURE_MIN=30
TEMPERATURE_MAX=35
HUMIDITY_MIN=30
LIGHT_MIN=200

EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=zaremabazarova11@gmail.com
SMTP_PASSWORD=<google_app_password>
SMTP_FROM_EMAIL=zaremabazarova11@gmail.com
SMTP_USE_TLS=true
```

Expose the backend publicly if the frontend is a separate Bult service.

Backend health check:

```text
https://<backend-public-url>/health
```

## Frontend Service

Git source:

```text
Repository: your GitHub repository
Context: .
Dockerfile: smart-plant-frontend/Dockerfile
```

Build argument:

```env
VITE_API_BASE_URL=https://<backend-public-url>/api/v1
```

If Bult does not have a build-args field, set this as an environment/build variable for the frontend service before build.

## IoT Gateway After Deployment

Use the deployed backend URL:

```powershell
cd "C:\Users\Admin\Downloads\smartsystem-new-report-updates\smartsystem-new-report-updates\iot\serial_gateway"

.\.venv\Scripts\python.exe serial_gateway.py --port COM3 --baud-rate 9600 --backend-url https://<backend-public-url> --device-id demo-sensor-001 --device-token "TOKEN_FROM_ADMIN" --source-label serial:COM3 --soil-dry-raw 1023 --log-level DEBUG
```

The gateway must use the same `device_id` and token that were created in the deployed admin panel.

## Important

Do not commit real passwords, database URLs with passwords, Gmail app passwords, or `.env` files to GitHub.
