from __future__ import annotations

import argparse
from datetime import datetime
import json
import random
import sys
import time
from typing import Any

import httpx


MODE_CHOICES = ("normal", "attention", "critical", "random", "cycle")
REQUIRED_DASHBOARD_FIELDS = (
    "condition_status",
    "health_score",
    "risk_factors",
    "confidence",
    "explanation",
    "ml_prediction",
    "ml_confidence",
    "class_probabilities",
    "analysis_method",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the full demo flow without real Arduino Uno USB Serial hardware."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--email", default="demo_user@example.com")
    parser.add_argument("--password", default="DemoPass123!")
    parser.add_argument("--admin-email", default="admin@example.com")
    parser.add_argument("--admin-password", default="AdminPass123!")
    parser.add_argument("--plant-name", default="Demo Golden Pothos")
    parser.add_argument("--sensor-device-id", default=None)
    parser.add_argument("--mode", choices=MODE_CHOICES, default="cycle")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--count", type=int, default=9)
    return parser


def random_float(start: float, stop: float) -> float:
    return round(random.uniform(start, stop), 1)


def redacted_token(token: str) -> str:
    if len(token) <= 10:
        return token
    return f"{token[:6]}...{token[-4:]}"


def timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def resolve_cycle_mode(selected_mode: str, reading_number: int) -> str:
    if selected_mode != "cycle":
        return selected_mode
    cycle_modes = ("normal", "attention", "critical")
    return cycle_modes[(reading_number - 1) % len(cycle_modes)]


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
            ["low_moisture", "high_temperature", "low_humidity", "low_light", "mixed_moderate"]
        )
        if scenario == "low_moisture":
            return {
                "moisture": random_float(22.0, 32.0),
                "temperature": random_float(21.0, 27.0),
                "humidity": random_float(40.0, 60.0),
                "light": random_float(320.0, 650.0),
            }
        if scenario == "high_temperature":
            return {
                "moisture": random_float(38.0, 60.0),
                "temperature": random_float(30.0, 34.0),
                "humidity": random_float(35.0, 55.0),
                "light": random_float(300.0, 650.0),
            }
        if scenario == "low_humidity":
            return {
                "moisture": random_float(38.0, 60.0),
                "temperature": random_float(22.0, 28.0),
                "humidity": random_float(25.0, 35.0),
                "light": random_float(300.0, 650.0),
            }
        if scenario == "low_light":
            return {
                "moisture": random_float(40.0, 62.0),
                "temperature": random_float(22.0, 28.0),
                "humidity": random_float(38.0, 60.0),
                "light": random_float(120.0, 220.0),
            }
        return {
            "moisture": random_float(22.0, 32.0),
            "temperature": random_float(30.0, 34.0),
            "humidity": random_float(25.0, 35.0),
            "light": random_float(120.0, 220.0),
        }
    if mode == "critical":
        scenario = random.choice(["dry_and_hot", "dark_and_dry", "low_humidity", "mixed_critical"])
        if scenario == "dry_and_hot":
            return {
                "moisture": random_float(5.0, 18.0),
                "temperature": random_float(36.0, 42.0),
                "humidity": random_float(15.0, 30.0),
                "light": random_float(140.0, 260.0),
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
                "moisture": random_float(16.0, 35.0),
                "temperature": random_float(35.0, 40.0),
                "humidity": random_float(10.0, 25.0),
                "light": random_float(90.0, 220.0),
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


def api_request(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    token: str | None = None,
    device_token: str | None = None,
    json_body: dict[str, Any] | None = None,
) -> httpx.Response:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if device_token:
        headers["X-Device-Token"] = device_token
    return client.request(method, url, headers=headers, json=json_body)


def safe_json(response: httpx.Response) -> dict[str, Any] | list[Any] | None:
    try:
        return response.json()
    except Exception:
        return None


def fail(message: str) -> int:
    print(f"FAILED: {message}")
    return 1


def ensure_backend_reachable(client: httpx.Client, base_url: str) -> None:
    try:
        response = client.get(f"{base_url.rstrip('/')}/health")
    except httpx.ConnectError as exc:
        raise RuntimeError(f"Backend is not reachable at {base_url}") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Backend health check failed: {exc}") from exc
    if response.status_code != 200:
        raise RuntimeError(f"Backend health check returned {response.status_code}")


def register_or_continue(
    client: httpx.Client,
    base_url: str,
    *,
    email: str,
    password: str,
) -> str:
    register_payload = {
        "full_name": "Demo User",
        "email": email,
        "password": password,
        "password_confirm": password,
    }
    response = api_request(client, "POST", f"{base_url.rstrip('/')}/api/v1/auth/register", json_body=register_payload)
    if response.status_code == 200:
        return "registered"
    if response.status_code == 409:
        return "existing_user"
    raise RuntimeError(f"Register failed: {response.status_code} {response.text}")


def login_and_get_session(client: httpx.Client, base_url: str, *, email: str, password: str) -> tuple[str, dict[str, Any]]:
    response = api_request(
        client,
        "POST",
        f"{base_url.rstrip('/')}/api/v1/auth/login",
        json_body={"email": email, "password": password},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Login failed: {response.status_code} {response.text}")
    payload = safe_json(response)
    if not isinstance(payload, dict) or not isinstance(payload.get("access_token"), str):
        raise RuntimeError("Login response did not include access_token")
    user = payload.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise RuntimeError("Login response did not include user id")
    return payload["access_token"], user


def create_demo_plant(
    client: httpx.Client,
    base_url: str,
    *,
    token: str,
    plant_name: str,
) -> dict[str, Any]:
    response = api_request(
        client,
        "POST",
        f"{base_url.rstrip('/')}/api/v1/plants",
        token=token,
        json_body={
            "name": plant_name,
            "species": "Epipremnum aureum",
            "location": "Demo dashboard",
            "description": "Auto-generated by run_full_demo_flow.py",
        },
    )
    if response.status_code != 200:
        raise RuntimeError(f"Create plant failed: {response.status_code} {response.text}")
    payload = safe_json(response)
    if not isinstance(payload, dict) or "id" not in payload:
        raise RuntimeError("Create plant response did not include plant id")
    return payload


def create_demo_sensor(
    client: httpx.Client,
    base_url: str,
    *,
    token: str,
    requested_device_id: str,
) -> dict[str, Any]:
    device_id = requested_device_id
    for attempt in range(2):
        response = api_request(
            client,
            "POST",
            f"{base_url.rstrip('/')}/api/v1/sensors",
            token=token,
            json_body={"device_id": device_id, "type": "multi"},
        )
        if response.status_code == 200:
            payload = safe_json(response)
            if (
                not isinstance(payload, dict)
                or not isinstance(payload.get("device_token"), str)
                or not isinstance(payload.get("sensor"), dict)
            ):
                raise RuntimeError("Create sensor response did not include sensor and device_token")
            return payload
        if response.status_code == 409 and attempt == 0:
            device_id = f"{requested_device_id}-{timestamp_suffix()}"
            continue
        raise RuntimeError(f"Create sensor failed: {response.status_code} {response.text}")
    raise RuntimeError("Create sensor failed after retry")


def attach_sensor(
    client: httpx.Client,
    base_url: str,
    *,
    token: str,
    sensor_id: int,
    plant_id: int,
) -> None:
    response = api_request(
        client,
        "POST",
        f"{base_url.rstrip('/')}/api/v1/sensors/{sensor_id}/attach",
        token=token,
        json_body={"plant_id": plant_id},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Attach sensor failed: {response.status_code} {response.text}")


def assign_sensor(
    client: httpx.Client,
    base_url: str,
    *,
    token: str,
    sensor_id: int,
    user_id: int,
) -> None:
    response = api_request(
        client,
        "POST",
        f"{base_url.rstrip('/')}/api/v1/sensors/{sensor_id}/assign",
        token=token,
        json_body={"user_id": user_id},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Assign sensor failed: {response.status_code} {response.text}")


def get_alerts_for_user(client: httpx.Client, base_url: str, *, token: str) -> list[dict[str, Any]]:
    response = api_request(client, "GET", f"{base_url.rstrip('/')}/api/v1/alerts", token=token)
    if response.status_code != 200:
        raise RuntimeError(f"Fetch alerts failed: {response.status_code} {response.text}")
    payload = safe_json(response)
    if not isinstance(payload, list):
        raise RuntimeError("Alerts response is not a list")
    return [item for item in payload if isinstance(item, dict)]


def get_dashboard(client: httpx.Client, base_url: str, *, token: str, plant_id: int) -> dict[str, Any]:
    response = api_request(
        client,
        "GET",
        f"{base_url.rstrip('/')}/api/v1/dashboard/plants/{plant_id}",
        token=token,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Fetch dashboard failed: {response.status_code} {response.text}")
    payload = safe_json(response)
    if not isinstance(payload, dict):
        raise RuntimeError("Dashboard response is not a JSON object")
    return payload


def verify_dashboard_payload(dashboard: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    if "current" not in dashboard or "history" not in dashboard:
        return {}, "Dashboard missing current or history"
    condition = dashboard.get("condition")
    if not isinstance(condition, dict):
        return {}, "Dashboard missing condition object"
    for field_name in REQUIRED_DASHBOARD_FIELDS:
        if field_name not in condition:
            return condition, f"Dashboard missing ML/condition field: {field_name}"
    return condition, None


def run_ingest_sequence(
    client: httpx.Client,
    base_url: str,
    *,
    device_id: str,
    device_token: str,
    selected_mode: str,
    interval: float,
    count: int,
) -> list[tuple[int, str, dict[str, float], int, str]]:
    events: list[tuple[int, str, dict[str, float], int, str]] = []
    for reading_number in range(1, count + 1):
        active_mode = resolve_cycle_mode(selected_mode, reading_number)
        payload = payload_for_mode(active_mode)
        response = api_request(
            client,
            "POST",
            f"{base_url.rstrip('/')}/api/v1/ingest/sensors/{device_id}/data",
            device_token=device_token,
            json_body=payload,
        )
        response_text = response.text
        events.append((reading_number, active_mode, payload, response.status_code, response_text))
        if response.status_code == 401:
            raise RuntimeError("Invalid or missing device token")
        if response.status_code == 404:
            raise RuntimeError("Check device_id or endpoint")
        if response.status_code != 200:
            raise RuntimeError(f"Ingest failed: {response.status_code} {response_text}")
        if reading_number < count and interval > 0:
            time.sleep(interval)
    return events


def main() -> int:
    args = build_parser().parse_args()
    if args.interval < 0:
        return fail("--interval must be zero or greater")
    if args.count < 1:
        return fail("--count must be at least 1")

    base_url = args.base_url.rstrip("/")
    token = ""
    dashboard: dict[str, Any] = {}
    condition: dict[str, Any] = {}
    alerts_after: list[dict[str, Any]] = []
    ingest_events: list[tuple[int, str, dict[str, float], int, str]] = []

    try:
        with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
            ensure_backend_reachable(client, base_url)

            register_state = register_or_continue(
                client,
                base_url,
                email=args.email,
                password=args.password,
            )
            token, user_payload = login_and_get_session(client, base_url, email=args.email, password=args.password)
            user_id = int(user_payload["id"])
            admin_token, _admin_payload = login_and_get_session(
                client,
                base_url,
                email=args.admin_email,
                password=args.admin_password,
            )

            plant_name = args.plant_name
            existing_plants_response = api_request(
                client,
                "GET",
                f"{base_url}/api/v1/plants",
                token=token,
            )
            if existing_plants_response.status_code == 200:
                plants_payload = safe_json(existing_plants_response)
                if isinstance(plants_payload, list) and any(
                    isinstance(item, dict) and item.get("name") == plant_name for item in plants_payload
                ):
                    plant_name = f"{args.plant_name} {timestamp_suffix()}"

            plant = create_demo_plant(client, base_url, token=token, plant_name=plant_name)
            plant_id = int(plant["id"])

            sensor_device_id = args.sensor_device_id or f"demo-sensor-{timestamp_suffix()}"
            sensor_payload = create_demo_sensor(
                client,
                base_url,
                token=admin_token,
                requested_device_id=sensor_device_id,
            )
            sensor = sensor_payload["sensor"]
            device_token = sensor_payload["device_token"]
            if not device_token:
                raise RuntimeError("Missing device_token in sensor create response")
            sensor_id = int(sensor["id"])
            actual_device_id = str(sensor["device_id"])

            assign_sensor(client, base_url, token=admin_token, sensor_id=sensor_id, user_id=user_id)
            attach_sensor(client, base_url, token=admin_token, sensor_id=sensor_id, plant_id=plant_id)

            alerts_before = get_alerts_for_user(client, base_url, token=token)
            alerts_before_count = len([item for item in alerts_before if item.get("plant_id") == plant_id])

            ingest_events = run_ingest_sequence(
                client,
                base_url,
                device_id=actual_device_id,
                device_token=device_token,
                selected_mode=args.mode,
                interval=args.interval,
                count=args.count,
            )

            dashboard = get_dashboard(client, base_url, token=token, plant_id=plant_id)
            condition, dashboard_error = verify_dashboard_payload(dashboard)
            if dashboard_error:
                raise RuntimeError(dashboard_error)

            alerts_after = get_alerts_for_user(client, base_url, token=token)
            plant_alerts_after = [item for item in alerts_after if item.get("plant_id") == plant_id]
            if args.mode in {"critical", "cycle"} and len(plant_alerts_after) <= alerts_before_count:
                raise RuntimeError("No alerts after critical readings")

            recommendation = dashboard.get("active_recommendation")
            recommendation_text = (
                recommendation.get("text")
                if isinstance(recommendation, dict) and isinstance(recommendation.get("text"), str)
                else None
            )

            print("Demo flow report")
            print(f"User state: {register_state}")
            print(f"User ID: {user_id}")
            print(f"Plant ID: {plant_id}")
            print(f"Sensor ID: {sensor_id}")
            print(f"Device ID: {actual_device_id}")
            print(f"Device token: {redacted_token(device_token)}")
            for reading_number, active_mode, payload, status_code, response_text in ingest_events:
                print(
                    f"Ingest #{reading_number}: mode={active_mode} status={status_code} "
                    f"payload={json.dumps(payload, ensure_ascii=True)} body={response_text}"
                )
            print(f"Final condition_status: {condition.get('condition_status')}")
            print(f"Health score: {condition.get('health_score')}")
            print(f"Risk factors: {condition.get('risk_factors')}")
            print(f"ML prediction: {condition.get('ml_prediction')}")
            print(f"ML confidence: {condition.get('ml_confidence')}")
            print(f"Analysis method: {condition.get('analysis_method')}")
            print(f"Active recommendation: {recommendation_text}")
            print(f"Alerts count for plant: {len(plant_alerts_after)}")
            print("Final result: PASSED")
            return 0

    except RuntimeError as exc:
        print(f"Demo flow error: {exc}")
        if dashboard:
            observed_fields = list((dashboard.get("condition") or {}).keys()) if isinstance(dashboard.get("condition"), dict) else []
            print(f"Observed condition fields before failure: {observed_fields}")
        if alerts_after:
            print(f"Observed alerts count before failure: {len(alerts_after)}")
        print("Final result: FAILED")
        return 1
    except KeyboardInterrupt:
        print("Demo flow interrupted by user")
        print("Final result: FAILED")
        return 130


if __name__ == "__main__":
    sys.exit(main())
