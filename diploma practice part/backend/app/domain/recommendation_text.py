"""
Template recommendations tied to each abnormal rule. Multiple issues are merged with context.
"""
from typing import List, Tuple

from app.domain.health_rules import AbnormalItem


TEMPLATES = {
    "low_soil_moisture": "Water the plant and check soil condition.",
    "high_temperature": "Move the plant away from direct heat or improve ventilation.",
    "low_humidity": "Increase air humidity or place water near the plant.",
    "low_light": "Move the plant to a brighter location.",
}


def build_recommendation_text(items: List[AbnormalItem]) -> Tuple[str, str]:
    if not items:
        return "No action needed for now.", "All measured values are within configured thresholds."
    recs: List[str] = []
    expl_parts: List[str] = []
    for it in items:
        recs.append(
            TEMPLATES.get(it.code, "Review the plant's environment and repeat measurements.")
        )
        expl_parts.append(f"{it.label}: {it.detail}")
    text = " ".join(recs)
    explanation = "Triggered by: " + " | ".join(expl_parts)
    return text, explanation
