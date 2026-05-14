"""add notification email preferences

Revision ID: 0005_email_prefs
Revises: 0004_user_notification_settings
Create Date: 2026-05-13 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_email_prefs"
down_revision: Union[str, Sequence[str], None] = "0004_user_notification_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_notification_settings",
        sa.Column("email_critical_alerts", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "user_notification_settings",
        sa.Column("email_moisture_alerts", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "user_notification_settings",
        sa.Column("email_temperature_alerts", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "user_notification_settings",
        sa.Column("email_humidity_alerts", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "user_notification_settings",
        sa.Column("email_light_alerts", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_column("user_notification_settings", "email_light_alerts")
    op.drop_column("user_notification_settings", "email_humidity_alerts")
    op.drop_column("user_notification_settings", "email_temperature_alerts")
    op.drop_column("user_notification_settings", "email_moisture_alerts")
    op.drop_column("user_notification_settings", "email_critical_alerts")
