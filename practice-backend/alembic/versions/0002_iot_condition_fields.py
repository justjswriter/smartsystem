"""iot security and condition support

Revision ID: 0002_iot_condition_fields
Revises: 0001_init_mvp_schema
Create Date: 2026-05-02 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_iot_condition_fields"
down_revision: Union[str, Sequence[str], None] = "0001_init_mvp_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sensors", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("sensors", sa.Column("device_token_hash", sa.String(length=255), nullable=True))
    op.add_column("sensors", sa.Column("last_ingest_source", sa.String(length=255), nullable=True))
    op.add_column("sensors", sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sensors", sa.Column("last_error_message", sa.Text(), nullable=True))
    op.create_foreign_key("fk_sensors_user_id_users", "sensors", "users", ["user_id"], ["id"])
    op.create_index("ix_sensors_user_id", "sensors", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sensors_user_id", table_name="sensors")
    op.drop_constraint("fk_sensors_user_id_users", "sensors", type_="foreignkey")
    op.drop_column("sensors", "last_error_message")
    op.drop_column("sensors", "last_error_at")
    op.drop_column("sensors", "last_ingest_source")
    op.drop_column("sensors", "device_token_hash")
    op.drop_column("sensors", "user_id")
