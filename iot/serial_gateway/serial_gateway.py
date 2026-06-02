from __future__ import annotations

import argparse
import json
import logging
import math
import sys
import time
from typing import Any

import httpx
import serial
from serial import SerialException


SOIL_WET_RAW = 0.0
SOIL_DRY_RAW = 220.0
LIGHT_RAW_MAX = 1023.0
LIGHT_SCORE_MAX = 1000.0
DEFAULT_HUMIDITY_OFFSET = 20.0


logger = logging.getLogger("serial_gateway")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read Arduino Uno JSON lines from USB Serial and forward readings to the FastAPI backend."
    )
    parser.add_argument("--port", required=True, help="Serial port, for example COM3 on Windows.")
    parser.add_argument("--baud-rate", type=int, default=9600, help="Serial baud rate. Default: 9600.")
    parser.add_argument(
        "--backend-url",
        required=True,
        help="Backend base URL without /api/v1, for example http://127.0.0.1:8000.",
    )
    parser.add_argument("--device-id", required=True, help="Registered backend sensor device_id.")
    parser.add_argument("--device-token", required=True, help="Device token shown when registering/rotating the sensor.")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Minimum seconds between backend sends. Default: 5.",
    )
    parser.add_argument(
        "--http-timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds. Default: 10.",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=5.0,
        help="Delay after backend/serial errors before retrying. Default: 5.",
    )
    parser.add_argument(
        "--arduino-reset-delay",
        type=float,
        default=2.0,
        help="Delay after opening serial port because Arduino resets on connect. Default: 2.",
    )
    parser.add_argument(
        "--source-label",
        default=None,
        help="Optional source label stored by backend, for example serial:COM3. Default: serial:<port>.",
    )
    parser.add_argument(
        "--humidity-offset",
        type=float,
        default=DEFAULT_HUMIDITY_OFFSET,
        help=(
            "Calibration offset added to DHT humidity percentage before sending. "
            "Default: 20 because inexpensive DHT modules often under-read in dry rooms. "
            "Use 0 when the sensor is calibrated."
        ),
    )
    parser.add_argument(
        "--soil-wet-raw",
        type=float,
        default=SOIL_WET_RAW,
        help=(
            "Raw soil sensor value for fully saturated soil/water. Default: 0 to avoid reporting "
            "lightly damp soil as 100%%. Calibrate with your sensor's wet reading when available."
        ),
    )
    parser.add_argument(
        "--soil-dry-raw",
        type=float,
        default=SOIL_DRY_RAW,
        help="Raw soil sensor value for dry soil/air. Default: 220 for the current Arduino demo sensor.",
    )
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def optional_number(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if not is_finite_number(value):
        raise ValueError(f"{field_name} must be a number or null")
    return float(value)


def parse_json_line(line: str) -> dict[str, Any] | None:
    line = line.replace("\x00", "").strip()
    if not line:
        return None
    start = line.find("{")
    end = line.rfind("}")
    if start != -1 and end != -1 and end > start:
        line = line[start : end + 1]
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as exc:
        logger.warning("Skipping non-JSON serial line: %r (%s)", line, exc)
        return None

    if not isinstance(payload, dict):
        logger.warning("Skipping JSON line because it is not an object: %r", line)
        return None
    return payload


def normalize_reading(
    raw: dict[str, Any],
    *,
    humidity_offset: float = DEFAULT_HUMIDITY_OFFSET,
    soil_wet_raw: float = SOIL_WET_RAW,
    soil_dry_raw: float = SOIL_DRY_RAW,
) -> dict[str, float | None]:
    if not is_finite_number(raw.get("soil_raw")):
        raise ValueError("soil_raw must be a finite number")
    if not is_finite_number(raw.get("light_raw")):
        raise ValueError("light_raw must be a finite number")

    soil_raw = float(raw["soil_raw"])
    light_raw = float(raw["light_raw"])
    humidity = optional_number(raw.get("humidity"), "humidity")
    temperature = optional_number(raw.get("temperature"), "temperature")

    if soil_wet_raw == soil_dry_raw:
        raise ValueError("soil_wet_raw and soil_dry_raw must be different")
    soil_min = min(soil_wet_raw, soil_dry_raw)
    soil_max = max(soil_wet_raw, soil_dry_raw)

    if soil_raw < soil_min or soil_raw > soil_max:
        logger.warning(
            "soil_raw %.1f is outside calibrated range %.0f..%.0f; value will be clamped",
            soil_raw,
            soil_min,
            soil_max,
        )
    if light_raw < 0 or light_raw > LIGHT_RAW_MAX:
        logger.warning(
            "light_raw %.1f is outside expected range 0..%.0f; value will be clamped",
            light_raw,
            LIGHT_RAW_MAX,
        )

    moisture = (soil_dry_raw - soil_raw) / (soil_dry_raw - soil_wet_raw) * 100.0
    light = light_raw / LIGHT_RAW_MAX * LIGHT_SCORE_MAX
    normalized_humidity = clamp(humidity + humidity_offset, 0.0, 100.0) if humidity is not None else None

    return {
        "moisture": round(clamp(moisture, 0.0, 100.0), 1),
        "temperature": round(temperature, 1) if temperature is not None else None,
        "humidity": round(normalized_humidity, 1) if normalized_humidity is not None else None,
        "light": round(clamp(light, 0.0, LIGHT_SCORE_MAX), 1),
    }


def ingest_url(backend_url: str, device_id: str) -> str:
    return f"{backend_url.rstrip('/')}/api/v1/ingest/sensors/{device_id}/data"


def send_reading(
    client: httpx.Client,
    url: str,
    token: str,
    payload: dict[str, float | None],
    source_label: str,
) -> bool:
    try:
        response = client.post(
            url,
            headers={
                "X-Device-Token": token,
                "X-Ingest-Source": source_label,
                "Content-Type": "application/json",
            },
            json=payload,
        )
    except httpx.TimeoutException:
        logger.error("Backend request timed out")
        return False
    except httpx.HTTPError as exc:
        logger.error("Backend is unavailable: %s", exc)
        return False

    if response.status_code == 200:
        body = response.json()
        logger.info(
            "Accepted by backend: sensor_data_id=%s payload=%s",
            body.get("sensor_data_id"),
            payload,
        )
        return True

    detail = response.text
    try:
        body = response.json()
        detail = str(body.get("detail", body))
    except ValueError:
        pass

    if response.status_code == 401:
        logger.error("Backend rejected the device token for this device_id: %s", detail)
    elif response.status_code == 400 and "not attached" in detail.lower():
        logger.error("Sensor is not attached to a plant. Attach it in the frontend Sensors page: %s", detail)
    elif response.status_code == 404:
        logger.error("Sensor device_id was not found in backend: %s", detail)
    else:
        logger.error("Backend returned HTTP %s: %s", response.status_code, detail)
    return False


def open_serial_port(port: str, baud_rate: int, reset_delay: float) -> serial.Serial:
    try:
        ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
    except SerialException as exc:
        raise RuntimeError(
            f"Could not open serial port {port}: {exc}. "
            "Close Arduino IDE Serial Monitor, verify the COM port, and try again."
        ) from exc

    logger.info("Opened serial port %s at %s baud", port, baud_rate)
    if reset_delay > 0:
        logger.info("Waiting %.1fs for Arduino reset after serial connect", reset_delay)
        time.sleep(reset_delay)
    return ser


def run(args: argparse.Namespace) -> int:
    url = ingest_url(args.backend_url, args.device_id)
    source_label = args.source_label or f"serial:{args.port}"
    last_send_at = 0.0

    try:
        ser = open_serial_port(args.port, args.baud_rate, args.arduino_reset_delay)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 2

    logger.info("Forwarding readings to %s with source %s", url, source_label)
    with ser, httpx.Client(timeout=args.http_timeout) as client:
        while True:
            try:
                raw_bytes = ser.readline()
            except SerialException as exc:
                logger.error("Serial read failed: %s", exc)
                time.sleep(args.retry_delay)
                continue

            if not raw_bytes:
                continue

            line = raw_bytes.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            logger.debug("Serial line: %s", line)
            raw_payload = parse_json_line(line)
            if raw_payload is None:
                continue

            try:
                payload = normalize_reading(
                    raw_payload,
                    humidity_offset=args.humidity_offset,
                    soil_wet_raw=args.soil_wet_raw,
                    soil_dry_raw=args.soil_dry_raw,
                )
            except ValueError as exc:
                logger.warning("Skipping invalid reading %s: %s", raw_payload, exc)
                continue

            now = time.monotonic()
            sleep_for = args.interval - (now - last_send_at)
            if sleep_for > 0:
                time.sleep(sleep_for)

            success = send_reading(client, url, args.device_token, payload, source_label)
            last_send_at = time.monotonic()
            if not success:
                time.sleep(args.retry_delay)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.log_level)
    try:
        return run(args)
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
