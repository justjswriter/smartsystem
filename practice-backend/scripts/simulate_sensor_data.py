from __future__ import annotations

import argparse
import json
import random
import sys
import time

import httpx


MODE_CHOICES = ("normal", "attention", "critical", "random", "cycle")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send simulated sensor readings to the existing plant ingest endpoint."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Backend base URL, for example http://127.0.0.1:8000",
    )
    parser.add_argument("--device-id", required=True, help="Registered sensor device_id")
    parser.add_argument("--device-token", required=True, help="One-time device token")
    parser.add_argument("--mode", default="random", choices=MODE_CHOICES, help="Simulation mode")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between readings",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="How many readings to send before stopping",
    )
    return parser


def random_float(start: float, stop: float) -> float:
    return round(random.uniform(start, stop), 1)


def payload_for_mode(mode: str) -> dict[str, float]:
    if mode == "normal":
        return {
            "moisture": random_float(40.0, 65.0),
            "temperature": random_float(20.0, 27.0),
            "humidity": random_float(40.0, 65.0),
            "light": random_float(300.0, 700.0),
        }
    if mode == "attention":
        scenario = random.choice(
            [
                "low_moisture",
                "high_temperature",
                "low_humidity",
                "low_light",
                "mixed_moderate",
            ]
        )
        if scenario == "low_moisture":
            return {
                "moisture": random_float(22.0, 32.0),
                "temperature": random_float(22.0, 28.0),
                "humidity": random_float(40.0, 60.0),
                "light": random_float(300.0, 650.0),
            }
        if scenario == "high_temperature":
            return {
                "moisture": random_float(40.0, 60.0),
                "temperature": random_float(30.0, 34.0),
                "humidity": random_float(38.0, 55.0),
                "light": random_float(300.0, 650.0),
            }
        if scenario == "low_humidity":
            return {
                "moisture": random_float(38.0, 60.0),
                "temperature": random_float(22.0, 28.0),
                "humidity": random_float(25.0, 35.0),
                "light": random_float(320.0, 650.0),
            }
        if scenario == "low_light":
            return {
                "moisture": random_float(38.0, 62.0),
                "temperature": random_float(22.0, 28.0),
                "humidity": random_float(40.0, 62.0),
                "light": random_float(120.0, 220.0),
            }
        return {
            "moisture": random_float(22.0, 32.0),
            "temperature": random_float(30.0, 34.0),
            "humidity": random_float(25.0, 35.0),
            "light": random_float(120.0, 220.0),
        }
    if mode == "critical":
        scenario = random.choice(
            [
                "dry_and_hot",
                "dark_and_dry",
                "low_humidity",
                "mixed_critical",
            ]
        )
        if scenario == "dry_and_hot":
            return {
                "moisture": random_float(5.0, 18.0),
                "temperature": random_float(36.0, 42.0),
                "humidity": random_float(18.0, 30.0),
                "light": random_float(160.0, 300.0),
            }
        if scenario == "dark_and_dry":
            return {
                "moisture": random_float(5.0, 18.0),
                "temperature": random_float(24.0, 32.0),
                "humidity": random_float(20.0, 35.0),
                "light": random_float(40.0, 150.0),
            }
        if scenario == "low_humidity":
            return {
                "moisture": random_float(18.0, 35.0),
                "temperature": random_float(34.0, 40.0),
                "humidity": random_float(10.0, 25.0),
                "light": random_float(100.0, 220.0),
            }
        return {
            "moisture": random_float(5.0, 18.0),
            "temperature": random_float(36.0, 42.0),
            "humidity": random_float(10.0, 25.0),
            "light": random_float(40.0, 150.0),
        }
    return {
        "moisture": random_float(0.0, 100.0),
        "temperature": random_float(10.0, 45.0),
        "humidity": random_float(5.0, 90.0),
        "light": random_float(0.0, 1000.0),
    }


def resolve_mode(selected_mode: str, reading_index: int) -> str:
    if selected_mode != "cycle":
        return selected_mode
    cycle_modes = ("normal", "attention", "critical")
    return cycle_modes[(reading_index - 1) % len(cycle_modes)]


def print_response_error(status_code: int, response_text: str) -> None:
    if status_code == 401:
        print("Invalid or missing device token")
        return
    if status_code == 404:
        print("Check device_id or endpoint")
        return
    print(f"Unexpected response body: {response_text}")


def send_reading(
    client: httpx.Client,
    *,
    base_url: str,
    device_id: str,
    device_token: str,
    payload: dict[str, float],
) -> httpx.Response:
    url = f"{base_url.rstrip('/')}/api/v1/ingest/sensors/{device_id}/data"
    return client.post(
        url,
        headers={
            "Content-Type": "application/json",
            "X-Device-Token": device_token,
        },
        json=payload,
    )


def validate_args(args: argparse.Namespace) -> None:
    if args.interval < 0:
        raise SystemExit("--interval must be zero or greater")
    if args.count < 1:
        raise SystemExit("--count must be at least 1")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    timeout = httpx.Timeout(10.0, connect=5.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            for reading_number in range(1, args.count + 1):
                active_mode = resolve_mode(args.mode, reading_number)
                payload = payload_for_mode(active_mode)
                print(f"Reading #{reading_number}")
                print(f"Mode/state: {active_mode}")
                print(f"Payload: {json.dumps(payload, ensure_ascii=True)}")
                try:
                    response = send_reading(
                        client,
                        base_url=args.base_url,
                        device_id=args.device_id,
                        device_token=args.device_token,
                        payload=payload,
                    )
                except httpx.ConnectError:
                    print(f"Backend is not reachable at {args.base_url}")
                    return 1
                except httpx.HTTPError as exc:
                    print(f"HTTP error while sending reading: {exc}")
                    return 1

                print(f"HTTP status code: {response.status_code}")
                print(f"Response body: {response.text}")
                if response.status_code != 200:
                    print_response_error(response.status_code, response.text)

                if reading_number < args.count and args.interval > 0:
                    time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Simulation interrupted by user")
        return 130

    print(f"Finished sending {args.count} reading(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
