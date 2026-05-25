"""add sensor data plant recorded index

Revision ID: 0010_sensor_data_plant_idx
Revises: 0009_user_avatar_url
Create Date: 2026-05-25
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0010_sensor_data_plant_idx"
down_revision: Union[str, None] = "0009_user_avatar_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_sensor_data_plant_recorded",
        "sensor_data",
        ["plant_id", "recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sensor_data_plant_recorded", table_name="sensor_data")
