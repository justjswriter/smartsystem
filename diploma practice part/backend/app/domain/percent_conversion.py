"""
Map raw ESP32 ADC values to human-readable 0-100% for soil moisture and light.
Calibrate MOISTURE_* and LIGHT_* env vars to match your hardware (diploma documentation).
"""
from app.core.config import Settings


def soil_moisture_raw_to_percent(raw: int, s: Settings) -> float:
    """
    Assumes: dry conditions yield higher raw ADC, wet conditions yield lower.
    If your sensor is inverted, swap MOISTURE_DRY_RAW and MOISTURE_WET_RAW in .env.
    """
    d, w = s.MOISTURE_DRY_RAW, s.MOISTURE_WET_RAW
    if d == w:
        return 50.0
    p = 100.0 * (d - float(raw)) / float(d - w)
    return max(0.0, min(100.0, p))


def light_raw_to_percent(raw: int, s: Settings) -> float:
    """
    Maps analog light level so that DARK -> low %, BRIGHT -> high %.
    Adjust LIGHT_DARK_RAW / LIGHT_BRIGHT_RAW to your LDR / resistor divider.
    """
    lo, hi = s.LIGHT_DARK_RAW, s.LIGHT_BRIGHT_RAW
    if lo == hi:
        return 50.0
    p = 100.0 * (float(raw) - lo) / float(hi - lo)
    return max(0.0, min(100.0, p))
