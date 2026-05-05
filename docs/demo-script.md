# Demo Script (7-10 Minutes)

This script is intended for diploma defense of the **final diploma prototype**.

## 0:00-1:00 — Project Context

- Introduce problem: home plants are often overwatered, underwatered, or kept in poor light.
- Present system objective: connected monitoring with actionable recommendations.
- Show architecture chain: sensor data -> API ingest -> storage -> condition evaluation -> alert/recommendation -> dashboard.

## 1:00-2:30 — Authentication and Plant Setup

- Login as user.
- Open plant list and create (or select) a plant.
- Explain that each plant can be linked to physical sensors.

## 2:30-4:00 — Sensor Registration and Secure Ingest

- Register a sensor in UI/API.
- Mention one-time `device_token` behavior.
- Show ingest endpoint format:
  - `POST /api/v1/ingest/sensors/{device_id}/data`
  - Header: `X-Device-Token`
  - Body: `moisture`, `temperature`, `humidity`, `light`, optional `recorded_at`
- Send one valid ingest sample and one invalid request without token (should fail with `401`).

## 4:00-5:30 — Dashboard and Condition Evaluation

- Open dashboard for the same plant.
- Show current readings and history.
- Highlight condition block:
  - `condition_status`
  - `health_score`
  - `risk_factors`
  - `confidence`
  - `explanation`
- Show active recommendation text and reason.

## 5:30-7:00 — Alerts and Lifecycle

- Open alerts list for the user.
- Show generated critical alert and recommendation.
- Open alert details and show transition history.
- Perform one transition (for example: `created -> viewed`) to demonstrate FSM behavior.

## 7:00-8:30 — Access Control and Admin View

- Demonstrate ownership restriction:
  - another user cannot open SSE dashboard stream for чужое plant (`403`).
- Show admin read-only monitoring pages/endpoints:
  - users
  - sensors
  - alerts
  - logs

## 8:30-10:00 — Final Summary

- Reiterate that the prototype covers full loop:
  - secure ingest
  - data persistence
  - explainable condition assessment
  - recommendation generation
  - alert lifecycle
  - RBAC and ownership controls
- End with practical impact for home plant monitoring and readiness for future extensions.
