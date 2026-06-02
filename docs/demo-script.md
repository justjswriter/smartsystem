# Demo Script (7-10 Minutes)

This script is intended for diploma defense of the final diploma prototype.

## 0:00-1:00 - Project Context

- Introduce problem: home plants are often overwatered, underwatered, or kept in poor light.
- Present system objective: connected monitoring with actionable recommendations.
- Show architecture chain: Arduino Uno -> USB Serial -> Python Serial Gateway -> FastAPI ingest -> PostgreSQL -> condition evaluation -> alerts/recommendations/notifications -> React dashboard.
- Mention that the frontend is Kazakh-first by default, with Russian and English support.

## 1:00-2:30 - Authentication and Plant Setup

- Login as user.
- Open plant list and create or select a plant.
- Explain that the current supported plant profile is Golden pothos / Epipremnum aureum.
- Explain that physical sensors are linked by admin provisioning.

## 2:30-4:00 - Admin Sensor Provisioning and Secure Ingest

- Log in as admin.
- Create/provision a sensor in Admin page or API.
- Copy the one-time `device_token`.
- Assign the sensor to the user and attach it to the user's plant.
- Return to the user account and show the read-only Sensors view.
- Show ingest endpoint format:
  - `POST /api/v1/ingest/sensors/{device_id}/data`
  - Header: `X-Device-Token`
  - Body: `moisture`, `temperature`, `humidity`, `light`, optional `recorded_at`
- Send one valid ingest sample and one invalid request without token. The invalid request should fail with `401`.

### Demo Sensor Simulator

Use the simulator when no real Arduino Uno USB Serial setup is connected:

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\practice-backend

..\.venv\Scripts\python.exe -m scripts.simulate_sensor_data `
  --device-id YOUR_DEVICE_ID `
  --device-token "YOUR_DEVICE_TOKEN" `
  --mode cycle `
  --interval 3 `
  --count 12
```

The simulator sends realistic demo telemetry to the same ingest endpoint used by the real gateway, so the dashboard, charts, condition output, recommendations, alerts, and notifications behave as in a live demo.

### Automatic Full Demo Flow

Use the full demo automation when you want one command to register/login as user, create a plant, provision/assign/attach a sensor as admin, capture the one-time device token, send simulated readings, and verify dashboard plus alerts:

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\practice-backend

..\.venv\Scripts\python.exe -m scripts.run_full_demo_flow `
  --mode cycle `
  --interval 2 `
  --count 9
```

## 4:00-5:30 - Dashboard and Condition Evaluation

- Open dashboard for the same plant.
- Show current readings and history.
- Highlight condition block:
  - `condition_status`
  - `health_score`
  - `risk_factors`
  - `confidence`
  - `explanation`
- Show active recommendation text and reason.

## 5:30-7:00 - Alerts, Notifications, and Lifecycle

- Open alerts list for the user.
- Show generated critical alert and recommendation.
- Open the notification bell/panel and show the persisted in-app notification created from the new alert.
- Mark one notification as read or use "read all".
- Open alert details and show transition history.
- Perform one transition, for example `created -> viewed`, to demonstrate FSM behavior.

## 7:00-8:30 - Access Control and Admin View

- Demonstrate ownership restriction:
  - another user cannot open SSE dashboard stream for another user's plant (`403`).
- Show admin monitoring and provisioning pages/endpoints:
  - users
  - sensors
  - alerts
  - logs
  - sensor create/assign/attach/detach/rotate token

## 8:30-10:00 - Final Summary

- Reiterate that the prototype covers full loop:
  - secure ingest
  - data persistence
  - explainable condition assessment
  - recommendation generation
  - alert lifecycle
  - persisted in-app notifications
  - RBAC and ownership controls
- End with practical impact for home plant monitoring and readiness for future extensions.
