from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.routers import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.security import hash_password
from app.domain.enums import UserRole
from app.infrastructure.models import User
from app.infrastructure.repositories import UserRepository


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        async with AsyncSessionLocal() as db:
            repo = UserRepository(db)
            existing = await repo.get_by_email(settings.ADMIN_EMAIL)
            if not existing:
                await repo.create(
                    full_name="System Admin",
                    email=settings.ADMIN_EMAIL,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                    role=UserRole.ADMIN,
                )
    yield


UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health", tags=["system"])
async def healthcheck():
    return {"status": "ok", "service": settings.APP_NAME}
