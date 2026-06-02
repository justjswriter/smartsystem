"""seed supported aroid plant care profiles

Revision ID: 0007_supported_aroid_profiles
Revises: 0006_plant_care_profiles
Create Date: 2026-05-14 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_supported_aroid_profiles"
down_revision: Union[str, Sequence[str], None] = "0006_plant_care_profiles"
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
    conn = op.get_bind()
    base = conn.execute(
        sa.text(
            """
            select thresholds, basic_care, gardener_advice, issues, stable_advice
            from plant_care_profiles
            where canonical_species = 'Epipremnum aureum'
            """
        )
    ).mappings().first()
    if not base:
        return

    shared = {
        "thresholds": base["thresholds"],
        "basic_care": base["basic_care"],
        "gardener_advice": base["gardener_advice"],
        "issues": base["issues"],
        "stable_advice": base["stable_advice"],
        "is_active": True,
    }
    rows = [
        {
            **shared,
            "slug": "philodendron_hederaceum",
            "canonical_species": "Philodendron hederaceum",
            "display_names": {
                "kk": "Жүрек жапырақты филодендрон",
                "ru": "Филодендрон сердцелистный",
                "en": "Heartleaf philodendron",
            },
        },
        {
            **shared,
            "slug": "scindapsus_pictus",
            "canonical_species": "Scindapsus pictus",
            "display_names": {
                "kk": "Сциндапсус / сатин потос",
                "ru": "Сциндапсус / сатиновый потос",
                "en": "Satin pothos / Scindapsus pictus",
            },
        },
        {
            **shared,
            "slug": "syngonium_podophyllum",
            "canonical_species": "Syngonium podophyllum",
            "display_names": {
                "kk": "Сингониум",
                "ru": "Сингониум",
                "en": "Arrowhead vine / Syngonium podophyllum",
            },
        },
    ]
    op.bulk_insert(plant_care_profiles, rows)


def downgrade() -> None:
    op.execute(
        """
        delete from plant_care_profiles
        where canonical_species in (
            'Philodendron hederaceum',
            'Scindapsus pictus',
            'Syngonium podophyllum'
        )
        """
    )
