"""
Initial database schema: users, plants, sensors, readings, alerts, recommendations.
Uses SQLAlchemy metadata to stay aligned with ORM models (single source of truth).
"""
from collections.abc import Sequence
from typing import Union

from sqlalchemy import create_engine

from app.core.config import get_settings
from app.core.database import Base
from app.models import *  # noqa: F401,F403  -- load all mappers

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _engine():
    u = get_settings().DATABASE_URL
    return create_engine(u)


def upgrade() -> None:
    eng = _engine()
    # Create ENUM types and tables as defined in SQLAlchemy models
    Base.metadata.create_all(bind=eng)


def downgrade() -> None:
    eng = _engine()
    Base.metadata.drop_all(bind=eng)
