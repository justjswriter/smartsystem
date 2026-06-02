"""add user notification settings

Revision ID: 0004_user_notification_settings
Revises: 0003_notifications
Create Date: 2026-05-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_user_notification_settings"
down_revision: Union[str, Sequence[str], None] = "0003_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_notification_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_email", sa.String(length=255), nullable=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("critical_only", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_notification_settings_user_id"),
    )
    op.create_index("ix_user_notification_settings_id", "user_notification_settings", ["id"], unique=False)
    op.create_index("ix_user_notification_settings_user_id", "user_notification_settings", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_notification_settings_user_id", table_name="user_notification_settings")
    op.drop_index("ix_user_notification_settings_id", table_name="user_notification_settings")
    op.drop_table("user_notification_settings")
