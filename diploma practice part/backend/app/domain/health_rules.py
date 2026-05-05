"""
Rule-based, explainable plant health checks for diploma reporting.
No ML here; thresholds come from config (env).
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.core.config import Settings
from app.models.alert import AlertSeverity


@dataclass
class AbnormalItem:
    code: str
    label: str
    detail: str  # which value and threshold, for "explainability"


def evaluate_reading(
    soil_moisture_percent: Optional[float],
    temperature: Optional[float],
    humidity: Optional[float],
    light_percent: Optional[float],
    s: Settings,
) -> Tuple[List[AbnormalItem], AlertSeverity]:
    """
    Returns a list of abnormal items and a combined severity.
    Count-based severity: 1 -> medium, 2 -> high, 3+ -> critical
    (single abnormal = medium / "warning" level in the UI; aligns with spec.)
    """
    items: List[AbnormalItem] = []

    if soil_moisture_percent is not None and soil_moisture_percent < s.MOISTURE_MIN:
        items.append(
            AbnormalItem(
                "low_soil_moisture",
                "low soil moisture",
                f"soil moisture {soil_moisture_percent:.1f}% < {s.MOISTURE_MIN}%",
            )
        )
    if temperature is not None and temperature > s.TEMPERATURE_MAX:
        items.append(
            AbnormalItem(
                "high_temperature",
                "high temperature",
                f"temperature {temperature:.1f}°C > {s.TEMPERATURE_MAX}°C",
            )
        )
    if humidity is not None and humidity < s.HUMIDITY_MIN:
        items.append(
            AbnormalItem(
                "low_humidity",
                "low humidity",
                f"humidity {humidity:.1f}% < {s.HUMIDITY_MIN}%",
            )
        )
    if light_percent is not None and light_percent < s.LIGHT_MIN:
        items.append(
            AbnormalItem(
                "low_light",
                "low light",
                f"light {light_percent:.1f}% < {s.LIGHT_MIN}%",
            )
        )
    n = len(items)
    if n == 0:
        return items, AlertSeverity.low
    if n == 1:
        sev = AlertSeverity.medium
    elif n == 2:
        sev = AlertSeverity.high
    else:
        sev = AlertSeverity.critical
    return items, sev


def build_alert_message(items: List[AbnormalItem]) -> str:
    if not items:
        return "All values within normal range."
    parts = [f"- {i.label} ({i.detail})" for i in items]
    return "Abnormal conditions detected:\n" + "\n".join(parts)
