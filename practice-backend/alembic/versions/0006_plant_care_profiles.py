"""add plant care profiles

Revision ID: 0006_plant_care_profiles
Revises: 0005_email_prefs
Create Date: 2026-05-14 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_plant_care_profiles"
down_revision: Union[str, Sequence[str], None] = "0005_email_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


plant_care_profiles = sa.table(
    "plant_care_profiles",
    sa.column("slug", sa.String),
    sa.column("canonical_species", sa.String),
    sa.column("display_names", sa.JSON),
    sa.column("thresholds", sa.JSON),
    sa.column("basic_care", sa.JSON),
    sa.column("gardener_advice", sa.JSON),
    sa.column("issues", sa.JSON),
    sa.column("stable_advice", sa.JSON),
    sa.column("is_active", sa.Boolean),
)


def upgrade() -> None:
    op.create_table(
        "plant_care_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("canonical_species", sa.String(length=255), nullable=False),
        sa.Column("display_names", sa.JSON(), nullable=False),
        sa.Column("thresholds", sa.JSON(), nullable=False),
        sa.Column("basic_care", sa.JSON(), nullable=False),
        sa.Column("gardener_advice", sa.JSON(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("stable_advice", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canonical_species"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_plant_care_profiles_id"), "plant_care_profiles", ["id"], unique=False)
    op.create_index(
        op.f("ix_plant_care_profiles_slug"), "plant_care_profiles", ["slug"], unique=True
    )
    op.create_index(
        op.f("ix_plant_care_profiles_canonical_species"),
        "plant_care_profiles",
        ["canonical_species"],
        unique=True,
    )

    profile = {
        "slug": "common_tropical_aroid_vines",
        "canonical_species": "Epipremnum aureum",
        "display_names": {
            "kk": "Алтын потос / Эпипремнум",
            "ru": "Золотой потос / Эпипремнум",
            "en": "Golden pothos / Epipremnum",
        },
        "thresholds": {
            "moisture": {"min": 35.0, "max": 75.0, "optimal_min": 45.0, "optimal_max": 65.0},
            "temperature": {"min": 18.0, "max": 30.0, "optimal_min": 20.0, "optimal_max": 27.0},
            "humidity": {"min": 40.0, "max": 80.0, "optimal_min": 50.0, "optimal_max": 70.0},
            "light": {"min": 40.0, "max": 320.0, "optimal_min": 45.0, "optimal_max": 180.0},
        },
        "basic_care": [
            {
                "icon": "water",
                "color": "blue",
                "title": "Сколько раз поливать",
                "text": "Не поливайте каждый день. Обычно достаточно 1-2 раза в неделю: когда верхние 2 см почвы подсохли, полейте 150-250 мл отстоянной воды.",
            },
            {
                "icon": "light",
                "color": "amber",
                "title": "Где держать",
                "text": "Держите рядом со светлым окном: лучше восточное или западное. Не ставьте под прямое полуденное солнце, листья могут получить ожог.",
            },
            {
                "icon": "humidity",
                "color": "green",
                "title": "Влажность воздуха",
                "text": "Держите подальше от батареи и сухого потока воздуха. Если воздух сухой, поставьте рядом поддон с водой или сгруппируйте растения.",
            },
            {
                "icon": "temperature",
                "color": "orange",
                "title": "Комнатные условия",
                "text": "Золотой потос любит тёплое стабильное место: примерно 20-27°C. Не ставьте рядом со сквозняком, кондиционером или батареей.",
            },
        ],
        "gardener_advice": [
            {
                "icon": "water",
                "color": "blue",
                "title": "Полив",
                "text": "Решение по поливу рассчитывается по текущей влажности почвы.",
            },
            {
                "icon": "light",
                "color": "amber",
                "title": "Свет",
                "text": "Решение по месту у окна рассчитывается по текущему показателю света.",
            },
            {
                "icon": "humidity",
                "color": "green",
                "title": "Воздух",
                "text": "Совет по воздуху рассчитывается по текущей влажности воздуха.",
            },
            {
                "icon": "temperature",
                "color": "orange",
                "title": "Где держать",
                "text": "Совет по месту рассчитывается по текущей температуре.",
            },
        ],
        "issues": {
            "low_moisture": {"metric": "moisture", "direction": "below", "threshold": 35.0},
            "high_moisture": {"metric": "moisture", "direction": "above", "threshold": 75.0},
            "low_temperature": {"metric": "temperature", "direction": "below", "threshold": 18.0},
            "high_temperature": {"metric": "temperature", "direction": "above", "threshold": 30.0},
            "low_humidity": {"metric": "humidity", "direction": "below", "threshold": 40.0},
            "low_light": {"metric": "light", "direction": "below", "threshold": 40.0},
        },
        "stable_advice": {
            "text": "Условия стабильны. Сохраняйте текущий режим ухода.",
            "reason": "Последние показатели находятся в подходящем диапазоне.",
        },
        "is_active": True,
    }
    op.bulk_insert(plant_care_profiles, [profile])


def downgrade() -> None:
    op.drop_index(op.f("ix_plant_care_profiles_canonical_species"), table_name="plant_care_profiles")
    op.drop_index(op.f("ix_plant_care_profiles_slug"), table_name="plant_care_profiles")
    op.drop_index(op.f("ix_plant_care_profiles_id"), table_name="plant_care_profiles")
    op.drop_table("plant_care_profiles")
