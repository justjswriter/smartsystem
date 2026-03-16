from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Practice Backend"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    LOG_LEVEL: str = "INFO"

    # Sensor thresholds for alert generation (MVP defaults).
    MOISTURE_MIN: float = 30.0
    TEMPERATURE_MAX: float = 35.0
    HUMIDITY_MIN: float = 30.0
    LIGHT_MIN: float = 200.0

    # Optional bootstrapped admin account.
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_MAX: int = 100
    SSE_HEARTBEAT_SECONDS: int = Field(default=15, ge=5, le=60)


settings = Settings()
