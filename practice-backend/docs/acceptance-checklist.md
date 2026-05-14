# Acceptance Checklist by User Story (Functional Prototype)

This checklist maps the implemented prototype to API endpoints, services, and database tables after Phase 3 and Phase 4A.

## US1 - Registration and Login

- **Endpoints**
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
- **Services**
  - `AuthService`
- **DB Tables**
  - `users`
  - `system_logs`

## US2 - Plant Profile Management

- **Endpoints**
  - `POST /api/v1/plants`
  - `GET /api/v1/plants`
  - `GET /api/v1/plants/{plant_id}`
  - `PATCH /api/v1/plants/{plant_id}`
  - `DELETE /api/v1/plants/{plant_id}`
- **Services**
  - `PlantService`
- **DB Tables**
  - `plants`
  - `system_logs`
- **Plant Knowledge Base**
  - Current supported plant profile: Golden pothos / Epipremnum aureum.

## US3 - Admin Sensor Provisioning and User Read-Only Sensor View

- **Endpoints**
  - `POST /api/v1/sensors` (admin-only, returns one-time `device_token`)
  - `GET /api/v1/sensors` (admin sees all; user sees assigned or attached-to-own-plant sensors)
  - `POST /api/v1/sensors/{sensor_id}/assign` (admin-only)
  - `POST /api/v1/sensors/{sensor_id}/attach` (admin-only)
  - `POST /api/v1/sensors/{sensor_id}/detach` (admin-only)
  - `POST /api/v1/sensors/{sensor_id}/rotate-token` (admin-only, returns one-time `device_token`)
- **Services**
  - `SensorService`
- **DB Tables**
  - `sensors`
  - `plants`
  - `system_logs`
- **Security**
  - IoT ingest uses `X-Device-Token`; only token hash is stored.
  - Regular users cannot create, attach, detach, or rotate sensor tokens.

## US4 - Dashboard and Current Plant Condition

- **Endpoints**
  - `GET /api/v1/dashboard/plants/{plant_id}?hours=...`
- **Services**
  - `MonitoringService`
- **DB Tables**
  - `sensor_data`
  - `plants`
- **Decision Support**
  - Dashboard returns `condition` with `condition_status`, `health_score`, `risk_factors`, `confidence`, and `explanation`.
  - Recommendations use current condition and the Golden pothos knowledge base.

## US5 - Critical Alert Creation

- **Endpoints**
  - `POST /api/v1/ingest/sensors/{device_id}/data`
  - `GET /api/v1/alerts`
- **Services**
  - `AlertService`
  - `RecommendationService`
  - `NotificationService`
- **DB Tables**
  - `sensor_data`
  - `alerts`
  - `alert_transitions`
  - `recommendations`
  - `notifications`
  - `system_logs`
- **Security**
  - Ingest requires `X-Device-Token`; failed auth is logged.
- **Notification Behavior**
  - A newly created alert creates a persisted in-app notification.
  - Duplicate readings for an already-open alert do not create notification spam.

## US6 - Recommendations

- **Endpoints**
  - `GET /api/v1/alerts`
  - `GET /api/v1/alerts/{alert_id}`
  - `GET /api/v1/dashboard/plants/{plant_id}?hours=...`
- **Services**
  - `RecommendationService`
  - `AlertService`
- **DB Tables**
  - `recommendations`
  - `alerts`
  - `plants`
- **UI/API**
  - Alert responses expose recommendation text.
  - Dashboard exposes the active recommendation and current condition.

## US7 - Alert Lifecycle and FSM

- **Endpoints**
  - `GET /api/v1/alerts`
  - `GET /api/v1/alerts/{alert_id}`
  - `POST /api/v1/alerts/{alert_id}/transition`
- **Filters**
  - `status`, `plant_id`, `severity`, `metric`
- **Services**
  - `AlertWorkflowService`
- **DB Tables**
  - `alerts`
  - `alert_transitions`
  - `system_logs`

## US7A - Persisted In-App Notifications

- **Endpoints**
  - `GET /api/v1/notifications?unread_only=false&limit=20&offset=0`
  - `POST /api/v1/notifications/{notification_id}/read`
  - `POST /api/v1/notifications/read-all`
- **Services**
  - `NotificationService`
- **DB Tables**
  - `notifications`
- **Security**
  - Notifications are scoped to the current user.
  - Users cannot read or mark another user's notifications as read.

## US8 - Admin Monitoring and Provisioning

- **Endpoints**
  - `GET /api/v1/admin/users`
  - `GET /api/v1/admin/sensors`
  - `GET /api/v1/admin/alerts`
  - `GET /api/v1/admin/logs`
- **UI**
  - `/admin` provides monitoring and sensor provisioning controls for admin role.
- **Services**
  - `AdminService`
- **DB Tables**
  - `users`
  - `sensors`
  - `alerts`
  - `system_logs`

## Cross-Cutting Demo Validation

- **SSE Endpoints**
  - `GET /api/v1/stream/alerts`
  - `GET /api/v1/stream/dashboard/{plant_id}`
  - `GET /api/v1/stream/notifications`
- **i18n**
  - Frontend is Kazakh-first by default.
  - Russian and English are available.
- **Hardware Flow**
  - Arduino Uno -> USB Serial -> Python Serial Gateway -> FastAPI -> PostgreSQL -> React frontend.
- **Migrations**
  - `0001_init_mvp_schema.py`
  - `0002_iot_condition_fields.py`
  - `0003_notifications.py`
- **Tests**
  - Backend test suite currently passes with 37 tests.
