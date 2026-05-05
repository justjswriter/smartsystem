"""
Application configuration from environment variables (Pydantic Settings).
All secrets and tunable thresholds for alerts live here.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Set DATABASE_URL in .env to your team Supabase (or any PostgreSQL) URL. No local DB in repo.
    # Defaults are placeholders only; copy .env.example to .env and paste the real string.
    DATABASE_URL: str = "postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def ensure_psycopg2_driver(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        s = v.strip()
        if s.startswith("postgres://") and not s.startswith("postgresql+"):
            s = s.replace("postgres://", "postgresql+psycopg2://", 1)
        elif s.startswith("postgresql://") and not s.startswith("postgresql+"):
            s = s.replace("postgresql://", "postgresql+psycopg2://", 1)
        return s

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Single shared key for all ESP32 devices (sent as x-api-key)
    DEVICE_API_KEY: str = "dev-device-key-change-in-production"

    # CORS: comma-separated or JSON array in .env; default allows Vite dev server
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Ingest: if true, create a sensor row when device_id is unknown
    ALLOW_AUTO_REGISTER_DEVICE: bool = True

    # Raw ADC calibration for percent conversion (soil: higher raw often = drier in many modules)
    MOISTURE_DRY_RAW: int = 4000
    MOISTURE_WET_RAW: int = 1500
    # Light: high raw = bright for typical LDR + divider on ESP32; adjust if your wiring is opposite
    LIGHT_DARK_RAW: int = 200
    LIGHT_BRIGHT_RAW: int = 4000

    # Rule thresholds (user-facing, explainable in README and diploma text)
    MOISTURE_MIN: float = 30.0
    TEMPERATURE_MAX: float = 30.0
    HUMIDITY_MIN: float = 35.0
    LIGHT_MIN: float = 25.0

    @property
    def cors_origins_list(self) -> List[str]:
        raw = self.CORS_ORIGINS.strip()
        if raw.startswith("["):
            import json
            return json.loads(raw)
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
