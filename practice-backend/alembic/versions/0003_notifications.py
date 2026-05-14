"""add persisted in-app notifications

Revision ID: 0003_notifications
Revises: 0002_iot_condition_fields
Create Date: 2026-05-11 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_notifications"
down_revision: Union[str, Sequence[str], None] = "0002_iot_condition_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


notification_type = sa.Enum(
    "plant_condition",
    "critical_alert",
    "sensor_stale",
    "sensor_subscription",
    name="notification_type",
)
notification_severity = sa.Enum("info", "warning", "critical", name="notification_severity")


def upgrade() -> None:
    bind = op.get_bind()
    notification_type.create(bind, checkfirst=True)
    notification_severity.create(bind, checkfirst=True)

    notification_type_no_create = postgresql.ENUM(
        "plant_condition",
        "critical_alert",
        "sensor_stale",
        "sensor_subscription",
        name="notification_type",
        create_type=False,
    )
    notification_severity_no_create = postgresql.ENUM(
        "info", "warning", "critical", name="notification_severity", create_type=False
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", notification_type_no_create, nullable=False),
        sa.Column("severity", notification_severity_no_create, nullable=False, server_default="info"),
        sa.Column("title_key", sa.String(length=255), nullable=False),
        sa.Column("message_key", sa.String(length=255), nullable=False),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("related_plant_id", sa.Integer(), nullable=True),
        sa.Column("related_alert_id", sa.Integer(), nullable=True),
        sa.Column("related_sensor_id", sa.Integer(), nullable=True),
        sa.Column("dedupe_key", sa.String(length=255), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["related_alert_id"], ["alerts.id"]),
        sa.ForeignKeyConstraint(["related_plant_id"], ["plants.id"]),
        sa.ForeignKeyConstraint(["related_sensor_id"], ["sensors.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_related_plant_id", "notifications", ["related_plant_id"], unique=False)
    op.create_index("ix_notifications_related_alert_id", "notifications", ["related_alert_id"], unique=False)
    op.create_index("ix_notifications_related_sensor_id", "notifications", ["related_sensor_id"], unique=False)
    op.create_index("ix_notifications_dedupe_key", "notifications", ["dedupe_key"], unique=False)
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"], unique=False)
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"], unique=False)
    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "read_at", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_user_dedupe_read",
        "notifications",
        ["user_id", "dedupe_key", "read_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_user_dedupe_read", table_name="notifications")
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_read_at", table_name="notifications")
    op.drop_index("ix_notifications_dedupe_key", table_name="notifications")
    op.drop_index("ix_notifications_related_sensor_id", table_name="notifications")
    op.drop_index("ix_notifications_related_alert_id", table_name="notifications")
    op.drop_index("ix_notifications_related_plant_id", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")

    bind = op.get_bind()
    notification_severity.drop(bind, checkfirst=True)
    notification_type.drop(bind, checkfirst=True)
