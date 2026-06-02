"""add user avatar url

Revision ID: 0009_user_avatar_url
Revises: 0008_fix_species_care_text
Create Date: 2026-05-15 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_user_avatar_url"
down_revision: Union[str, Sequence[str], None] = "0008_fix_species_care_text"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
