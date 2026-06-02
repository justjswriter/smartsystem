"""
FastAPI application entry point: wires routers, CORS, and global exception handling.
Run with: `uvicorn app.main:app --reload --port 8001` from the `backend` directory.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.core.config import get_settings
from app.api.routers import auth, plants, sensors, readings, alerts, dashboard

log = logging.getLogger("app")

settings = get_settings()
app = FastAPI(
    title="Plant monitoring IoT API",
    description="Bachelor project: plant sensors, readings, rule-based AI alerts, dashboard.",
    version="1.0.0",
)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
    log.error("Database error (operational): %s", exc, exc_info=True)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database is unavailable. Check DATABASE_URL in .env and that your host (e.g. Supabase) is reachable."
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(plants.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(readings.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
