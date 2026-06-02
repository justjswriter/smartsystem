"""init mvp schema

Revision ID: 0001_init_mvp_schema
Revises:
Create Date: 2026-03-16 09:25:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0001_init_mvp_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = sa.Enum("user", "admin", name="user_role")
sensor_type = sa.Enum("soil_moisture", "temperature", "air_humidity", "light", "multi", name="sensor_type")
sensor_status = sa.Enum("offline", "online", "disabled", name="sensor_status")
alert_status = sa.Enum("created", "viewed", "acknowledged", "resolved", "closed", name="alert_status")
alert_severity = sa.Enum("low", "medium", "high", "critical", name="alert_severity")
alert_status_transition_from = sa.Enum(
    "created", "viewed", "acknowledged", "resolved", "closed", name="alert_status_transition_from"
)
alert_status_transition_to = sa.Enum(
    "created", "viewed", "acknowledged", "resolved", "closed", name="alert_status_transition_to"
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    sensor_type.create(bind, checkfirst=True)
    sensor_status.create(bind, checkfirst=True)
    alert_status.create(bind, checkfirst=True)
    alert_severity.create(bind, checkfirst=True)
    alert_status_transition_from.create(bind, checkfirst=True)
    alert_status_transition_to.create(bind, checkfirst=True)

    user_role_no_create = postgresql.ENUM("user", "admin", name="user_role", create_type=False)
    sensor_type_no_create = postgresql.ENUM(
        "soil_moisture", "temperature", "air_humidity", "light", "multi", name="sensor_type", create_type=False
    )
    sensor_status_no_create = postgresql.ENUM(
        "offline", "online", "disabled", name="sensor_status", create_type=False
    )
    alert_status_no_create = postgresql.ENUM(
        "created", "viewed", "acknowledged", "resolved", "closed", name="alert_status", create_type=False
    )
    alert_severity_no_create = postgresql.ENUM(
        "low", "medium", "high", "critical", name="alert_severity", create_type=False
    )
    alert_status_transition_from_no_create = postgresql.ENUM(
        "created", "viewed", "acknowledged", "resolved", "closed", name="alert_status_transition_from", create_type=False
    )
    alert_status_transition_to_no_create = postgresql.ENUM(
        "created", "viewed", "acknowledged", "resolved", "closed", name="alert_status_transition_to", create_type=False
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_no_create, nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("species", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_plants_user_id", "plants", ["user_id"], unique=False)

    op.create_table(
        "sensors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(length=255), nullable=False),
        sa.Column("type", sensor_type_no_create, nullable=False, server_default="multi"),
        sa.Column("status", sensor_status_no_create, nullable=False, server_default="offline"),
        sa.Column("plant_id", sa.Integer(), sa.ForeignKey("plants.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_sensors_device_id", "sensors", ["device_id"], unique=True)
    op.create_index("ix_sensors_plant_id", "sensors", ["plant_id"], unique=False)

    op.create_table(
        "sensor_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sensor_id", sa.Integer(), sa.ForeignKey("sensors.id"), nullable=False),
        sa.Column("plant_id", sa.Integer(), sa.ForeignKey("plants.id"), nullable=False),
        sa.Column("moisture", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("light", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_sensor_data_sensor_id", "sensor_data", ["sensor_id"], unique=False)
    op.create_index("ix_sensor_data_plant_id", "sensor_data", ["plant_id"], unique=False)
    op.create_index("ix_sensor_data_recorded_at", "sensor_data", ["recorded_at"], unique=False)
    op.create_index(
        "ix_sensor_data_sensor_recorded",
        "sensor_data",
        ["sensor_id", "recorded_at"],
        unique=False,
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plant_id", sa.Integer(), sa.ForeignKey("plants.id"), nullable=False),
        sa.Column("sensor_id", sa.Integer(), sa.ForeignKey("sensors.id"), nullable=True),
        sa.Column("status", alert_status_no_create, nullable=False, server_default="created"),
        sa.Column("severity", alert_severity_no_create, nullable=False, server_default="medium"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metric", sa.String(length=50), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"], unique=False)
    op.create_index("ix_alerts_plant_id", "alerts", ["plant_id"], unique=False)
    op.create_index("ix_alerts_sensor_id", "alerts", ["sensor_id"], unique=False)
    op.create_index(
        "ix_alerts_user_status_created",
        "alerts",
        ["user_id", "status", "created_at"],
        unique=False,
    )

    op.create_table(
        "alert_transitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("from_status", alert_status_transition_from_no_create, nullable=False),
        sa.Column("to_status", alert_status_transition_to_no_create, nullable=False),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_alert_transitions_alert_id", "alert_transitions", ["alert_id"], unique=False)

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plant_id", sa.Integer(), sa.ForeignKey("plants.id"), nullable=False),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_recommendations_plant_id", "recommendations", ["plant_id"], unique=False)

    op.create_table(
        "system_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_system_logs_event_type", "system_logs", ["event_type"], unique=False)
    op.create_index("ix_system_logs_created_at", "system_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_system_logs_created_at", table_name="system_logs")
    op.drop_index("ix_system_logs_event_type", table_name="system_logs")
    op.drop_table("system_logs")

    op.drop_index("ix_recommendations_plant_id", table_name="recommendations")
    op.drop_table("recommendations")

    op.drop_index("ix_alert_transitions_alert_id", table_name="alert_transitions")
    op.drop_table("alert_transitions")

    op.drop_index("ix_alerts_user_status_created", table_name="alerts")
    op.drop_index("ix_alerts_sensor_id", table_name="alerts")
    op.drop_index("ix_alerts_plant_id", table_name="alerts")
    op.drop_index("ix_alerts_user_id", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_sensor_data_sensor_recorded", table_name="sensor_data")
    op.drop_index("ix_sensor_data_recorded_at", table_name="sensor_data")
    op.drop_index("ix_sensor_data_plant_id", table_name="sensor_data")
    op.drop_index("ix_sensor_data_sensor_id", table_name="sensor_data")
    op.drop_table("sensor_data")

    op.drop_index("ix_sensors_plant_id", table_name="sensors")
    op.drop_index("ix_sensors_device_id", table_name="sensors")
    op.drop_table("sensors")

    op.drop_index("ix_plants_user_id", table_name="plants")
    op.drop_table("plants")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    alert_status_transition_to.drop(bind, checkfirst=True)
    alert_status_transition_from.drop(bind, checkfirst=True)
    alert_severity.drop(bind, checkfirst=True)
    alert_status.drop(bind, checkfirst=True)
    sensor_status.drop(bind, checkfirst=True)
    sensor_type.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
