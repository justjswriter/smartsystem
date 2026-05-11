from fastapi import APIRouter

from . import admin, alerts, auth, ingest, monitoring, notifications, plants, sensors, stream

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(plants.router)
api_router.include_router(sensors.router)
api_router.include_router(monitoring.router)
api_router.include_router(ingest.router)
api_router.include_router(alerts.router)
api_router.include_router(notifications.router)
api_router.include_router(stream.router)
api_router.include_router(admin.router)
