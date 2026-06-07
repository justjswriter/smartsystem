"""store plant image data urls

Revision ID: 0011_plant_image_url_text
Revises: 0010_sensor_data_plant_idx
Create Date: 2026-06-07
"""

from typing import Union

import sqlalchemy as sa
from alembic import op


revision: str = "0011_plant_image_url_text"
down_revision: Union[str, None] = "0010_sensor_data_plant_idx"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("plants", "image_url", existing_type=sa.String(length=1024), type_=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("plants", "image_url", existing_type=sa.Text(), type_=sa.String(length=1024), nullable=True)
