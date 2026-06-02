"""fix species-specific plant care text

Revision ID: 0008_fix_species_care_text
Revises: 0007_supported_aroid_profiles
Create Date: 2026-05-14 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_fix_species_care_text"
down_revision: Union[str, Sequence[str], None] = "0007_supported_aroid_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SPECIES_TEXT = {
    "Philodendron hederaceum": "\u0424\u0438\u043b\u043e\u0434\u0435\u043d\u0434\u0440\u043e\u043d \u0441\u0435\u0440\u0434\u0446\u0435\u043b\u0438\u0441\u0442\u043d\u044b\u0439 \u043b\u044e\u0431\u0438\u0442 \u0442\u0451\u043f\u043b\u043e\u0435 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e\u0435 \u043c\u0435\u0441\u0442\u043e: \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u043e 20-27\u00b0C. \u041d\u0435 \u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0440\u044f\u0434\u043e\u043c \u0441\u043e \u0441\u043a\u0432\u043e\u0437\u043d\u044f\u043a\u043e\u043c, \u043a\u043e\u043d\u0434\u0438\u0446\u0438\u043e\u043d\u0435\u0440\u043e\u043c \u0438\u043b\u0438 \u0431\u0430\u0442\u0430\u0440\u0435\u0435\u0439.",
    "Scindapsus pictus": "\u0421\u0446\u0438\u043d\u0434\u0430\u043f\u0441\u0443\u0441 \u043b\u044e\u0431\u0438\u0442 \u0442\u0451\u043f\u043b\u043e\u0435 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e\u0435 \u043c\u0435\u0441\u0442\u043e: \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u043e 20-27\u00b0C. \u041d\u0435 \u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0440\u044f\u0434\u043e\u043c \u0441\u043e \u0441\u043a\u0432\u043e\u0437\u043d\u044f\u043a\u043e\u043c, \u043a\u043e\u043d\u0434\u0438\u0446\u0438\u043e\u043d\u0435\u0440\u043e\u043c \u0438\u043b\u0438 \u0431\u0430\u0442\u0430\u0440\u0435\u0435\u0439.",
    "Syngonium podophyllum": "\u0421\u0438\u043d\u0433\u043e\u043d\u0438\u0443\u043c \u043b\u044e\u0431\u0438\u0442 \u0442\u0451\u043f\u043b\u043e\u0435 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e\u0435 \u043c\u0435\u0441\u0442\u043e: \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u043e 20-27\u00b0C. \u041d\u0435 \u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0440\u044f\u0434\u043e\u043c \u0441\u043e \u0441\u043a\u0432\u043e\u0437\u043d\u044f\u043a\u043e\u043c, \u043a\u043e\u043d\u0434\u0438\u0446\u0438\u043e\u043d\u0435\u0440\u043e\u043c \u0438\u043b\u0438 \u0431\u0430\u0442\u0430\u0440\u0435\u0435\u0439.",
}

POTHOS_TEXT = "\u0417\u043e\u043b\u043e\u0442\u043e\u0439 \u043f\u043e\u0442\u043e\u0441 \u043b\u044e\u0431\u0438\u0442 \u0442\u0451\u043f\u043b\u043e\u0435 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e\u0435 \u043c\u0435\u0441\u0442\u043e: \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u043e 20-27\u00b0C. \u041d\u0435 \u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0440\u044f\u0434\u043e\u043c \u0441\u043e \u0441\u043a\u0432\u043e\u0437\u043d\u044f\u043a\u043e\u043c, \u043a\u043e\u043d\u0434\u0438\u0446\u0438\u043e\u043d\u0435\u0440\u043e\u043c \u0438\u043b\u0438 \u0431\u0430\u0442\u0430\u0440\u0435\u0435\u0439."


def upgrade() -> None:
    conn = op.get_bind()
    for species, text in SPECIES_TEXT.items():
        conn.execute(
            sa.text(
                """
            update plant_care_profiles
            set basic_care = jsonb_set(basic_care::jsonb, '{3,text}', to_jsonb(cast(:care_text as text)))::json
            where canonical_species = :species
            """
            ),
            {"care_text": text, "species": species},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for species in SPECIES_TEXT:
        conn.execute(
            sa.text(
                """
            update plant_care_profiles
            set basic_care = jsonb_set(basic_care::jsonb, '{3,text}', to_jsonb(cast(:care_text as text)))::json
            where canonical_species = :species
            """
            ),
            {"care_text": POTHOS_TEXT, "species": species},
        )
