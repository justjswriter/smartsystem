# Chapter 3 Technical Verification Report

## 1. Repository Scope Check

| path | active / legacy / unclear | purpose | evidence | should be used in Chapter 3: yes/no |
|---|---|---|---|---|
| `practice-backend/` | active | FastAPI backend, models, services, routers, migrations, tests | `practice-backend/app/main.py`, `practice-backend/README.md` | yes |
| `smart-plant-frontend/` | active | React + TypeScript dashboard | `smart-plant-frontend/package.json`, `src/router.tsx` | yes |
| `iot/serial_gateway/` | active | Python USB serial gateway | `serial_gateway.py`, `README.md`, tests | yes |
| `iot/arduino_uno_sensor_node/` | active | Arduino Uno firmware | `arduino_uno_sensor_node.ino` says Arduino Uno, 9600 baud | yes |
| `practice-backend/alembic/` | active | PostgreSQL migrations | versions `0001` through `0008` | yes |
| `practice-backend/app/ml/` | active | Random Forest training artifacts and service inputs | `train_condition_model.py`, `plant_condition_model.joblib`, `model_metadata.json` | yes |
| `practice-backend/tests/` | active | Backend automated tests | 53 tests passed with `.venv\Scripts\python -m pytest -q` | yes |
| `iot/serial_gateway/tests/` | active but dependency gap in current env | Gateway unit tests | `test_serial_gateway.py`; current `.venv` lacks `pytest` | yes, with caveat |
| `docs/` | active documentation | Verification/demo/AI docs | `docs/ai-module.md`, `final-verification-report.md` | yes as supporting evidence |
| `diploma practice part/` | legacy | Older backend/frontend/ESP32 implementation | separate backend/frontend and `firmware/esp32_plant_monitor` | no |
| `diploma-latex/` | thesis source, not implementation | LaTeX chapter files | `chapters/03-practical-part.tex` | yes only for thesis editing context |

## 2. Technology Stack Verification

| technology area | actual tool/library | version if found | file evidence | whether Chapter 3 wording is accurate |
|---|---:|---:|---|---|
| backend framework | FastAPI | 0.135.1 | root `requirements.txt` | accurate |
| ASGI server | Uvicorn | 0.41.0 | root `requirements.txt` | accurate |
| database | PostgreSQL | Docker image `postgres:17.1-alpine` | `practice-backend/docker-compose.yml` | accurate |
| ORM | SQLAlchemy | 2.0.48 | root `requirements.txt` | accurate |
| database driver | asyncpg | 0.31.0 | root `requirements.txt`, `DATABASE_URL=postgresql+asyncpg` | accurate |
| migration tool | Alembic | 1.18.4 | root `requirements.txt`, `alembic.ini` | accurate |
| validation | Pydantic / pydantic-settings | 2.12.5 / 2.13.1 | root `requirements.txt` | accurate |
| user JWT | python-jose | 3.5.0 | `core/security.py` | accurate |
| password/device token hashing | bcrypt | 5.0.0 | `core/security.py` | accurate |
| frontend framework | React | ^19.2.4 | `smart-plant-frontend/package.json` | accurate |
| frontend language | TypeScript | ~5.9.3 | `package.json`, `.tsx` files | accurate |
| build tool | Vite | ^8.0.1, build ran with 8.0.3 | `package.json`, build output | accurate |
| charting | Recharts | ^3.8.1 | `package.json`, `Analytics.tsx`, `PlantDetails.tsx` | accurate |
| SSE client | `@microsoft/fetch-event-source` | ^2.0.1 | `package.json`, `AppStateContext.tsx`, `PlantDetailsPage.tsx` | accurate |
| SSE server | sse-starlette | 3.3.2 | root `requirements.txt`, `stream.py` | accurate |
| ML library | scikit-learn | 1.7.2 | root `requirements.txt`, `train_condition_model.py` | accurate |
| model persistence | joblib | 1.5.2 | root `requirements.txt`, `ml_condition_service.py` | accurate |
| serial communication | pyserial | >=3.5,<4 | `iot/serial_gateway/requirements.txt` | accurate |
| gateway HTTP client | httpx | >=0.28,<1 | gateway requirements | accurate |
| tests | pytest, pytest-asyncio, unittest | pytest 9.0.2 in root deps; gateway uses unittest style | tests folders | accurate with caveat |
| local runtime | Docker Compose, Node/npm, Python venv | found | `docker-compose.yml`, README, package scripts | accurate |

## 3. Architecture Verification

| architecture element | implemented / partially implemented / not found | files/classes/functions | evidence | safe thesis wording |
|---|---|---|---|---|
| client-server architecture | implemented | React frontend, FastAPI backend | separate `smart-plant-frontend` and `practice-backend` | “client-server web application” |
| REST API | implemented | routers under `app/api/v1/routers` | CRUD/list/action endpoints | “REST-style API” |
| Server-Sent Events | implemented | `stream.py`, `event_bus.py` | `/stream/alerts`, `/stream/dashboard/{plant_id}`, `/stream/notifications` | “near real-time updates using SSE” |
| layered backend architecture | implemented | api/application/domain/infrastructure/core | README and directory layout | “layered architecture” |
| API/router layer | implemented | `auth.py`, `plants.py`, etc. | APIRouter files | safe |
| service layer | implemented | `AuthService`, `AlertService`, `MonitoringService` | `app/application/services` | safe |
| repository layer | implemented | `SensorRepository`, `PlantRepository`, etc. | `app/infrastructure/repositories` | safe |
| domain/enums/plant knowledge layer | implemented | `domain/enums/common.py`, `plant_knowledge/profiles.py` | enums and thresholds | safe |
| infrastructure/database layer | implemented | `core/database.py`, ORM models | async engine/session, models | safe |
| dependency injection | implemented | `Depends(get_db)`, `Depends(get_current_user)` | routers/deps | safe |
| middleware | implemented | `RequestLoggingMiddleware`, CORS | `main.py`, `middleware.py` | safe |
| async endpoints | implemented | router functions use `async def` | routers | safe |
| Pydantic schemas | implemented | `app/application/schemas` | request/response models | safe |
| request logging | implemented | request ID, elapsed time | `core/middleware.py` | safe |
| persistent audit/system logs | partially implemented | `system_logs`, `SystemLogRepository` | selected events only | “selected system events are persisted” |
| event bus | implemented | in-memory async queues | `event_bus.py` | “in-memory event bus for SSE notifications” |
| frontend protected routes | implemented | `ProtectedLayout` | redirects unauthenticated users | safe |
| frontend role-based UI | partially implemented | admin nav and page redirect | UI hides admin link; backend enforces admin | “admin UI is conditionally shown and backend protected” |
| frontend API client | implemented | `src/api.ts` | central fetch wrapper | safe |

## 4. Backend API Verification

Base prefix is `/api/v1` except `/health`.

| HTTP method | full path | router file | function name | request schema | response schema | auth required | required role | purpose | should be mentioned in Chapter 3 |
|---|---|---|---|---|---|---|---|---|---|
| POST | `/api/v1/auth/register` | `auth.py` | `register` | `RegisterRequest` | `UserResponse` | no | None | user registration | yes |
| POST | `/api/v1/auth/login` | `auth.py` | `login` | `LoginRequest` | `TokenResponse` | no | None | login/JWT | yes |
| GET | `/api/v1/auth/me` | `auth.py` | `me` | none | `UserResponse` | yes | User/Admin | current user | yes |
| POST | `/api/v1/plants` | `plants.py` | `create_plant` | `PlantCreate` | `PlantResponse` | yes | User/Admin | create plant | yes |
| GET | `/api/v1/plants` | `plants.py` | `list_plants` | none | `list[PlantResponse]` | yes | User/Admin | list own plants | yes |
| GET | `/api/v1/plants/{plant_id}` | `plants.py` | `get_plant` | none | `PlantResponse` | yes | owner | plant detail | yes |
| PATCH | `/api/v1/plants/{plant_id}` | `plants.py` | `update_plant` | `PlantUpdate` | `PlantResponse` | yes | owner | update plant | yes |
| POST | `/api/v1/plants/{plant_id}/photo` | `plants.py` | `upload_plant_photo` | multipart file | `PlantResponse` | yes | owner | photo upload | optional |
| DELETE | `/api/v1/plants/{plant_id}` | `plants.py` | `delete_plant` | none | status dict | yes | owner | soft delete plant | yes |
| GET | `/api/v1/plant-care-profiles` | `plant_care_profiles.py` | `list_plant_care_profiles` | none | `list[PlantCareProfileResponse]` | yes | User/Admin | available care profiles | yes |
| GET | `/api/v1/plant-care-profiles/resolve` | `plant_care_profiles.py` | `resolve_plant_care_profile` | `species` query | `PlantCareProfileResponse \| None` | yes | User/Admin | resolve profile | optional |
| POST | `/api/v1/sensors` | `sensors.py` | `create_sensor` | `SensorCreate` | `SensorProvisionResponse` | yes | Admin | provision sensor/token | yes |
| GET | `/api/v1/sensors` | `sensors.py` | `list_sensors` | query limit/offset | `list[SensorResponse]` | yes | User/Admin | list visible sensors | yes |
| POST | `/api/v1/sensors/{sensor_id}/assign` | `sensors.py` | `assign_sensor` | `SensorAssignRequest` | `SensorResponse` | yes | Admin | assign sensor to user | yes |
| POST | `/api/v1/sensors/{sensor_id}/attach` | `sensors.py` | `attach_sensor` | `SensorAttachRequest` | `SensorResponse` | yes | Admin | attach sensor to plant | yes |
| POST | `/api/v1/sensors/{sensor_id}/detach` | `sensors.py` | `detach_sensor` | none | `SensorResponse` | yes | Admin | detach sensor | yes |
| POST | `/api/v1/sensors/{sensor_id}/rotate-token` | `sensors.py` | `rotate_sensor_token` | none | `SensorProvisionResponse` | yes | Admin | rotate device token | yes |
| POST | `/api/v1/ingest/sensors/{device_id}/data` | `ingest.py` | `ingest_sensor_data` | `SensorDataIngest` | status dict | device token | Device | sensor data ingestion | yes |
| GET | `/api/v1/dashboard/plants/{plant_id}` | `monitoring.py` | `get_dashboard` | `hours` query | `DashboardResponse` | yes | owner | dashboard data | yes |
| GET | `/api/v1/alerts` | `alerts.py` | `list_alerts` | query filters | `list[AlertResponse]` | yes | User/Admin scoped | alerts | yes |
| GET | `/api/v1/alerts/{alert_id}` | `alerts.py` | `get_alert` | none | `AlertDetailResponse` | yes | owner | alert detail/history | yes |
| POST | `/api/v1/alerts/{alert_id}/transition` | `alerts.py` | `transition_alert` | `AlertTransitionRequest` | `AlertTransitionResponse` | yes | owner | alert lifecycle | yes |
| GET | `/api/v1/notifications` | `notifications.py` | `list_notifications` | query | `list[NotificationResponse]` | yes | User/Admin scoped | notifications | optional |
| POST | `/api/v1/notifications/{notification_id}/read` | `notifications.py` | `mark_notification_read` | none | `NotificationResponse` | yes | owner | mark read | optional |
| POST | `/api/v1/notifications/read-all` | `notifications.py` | `mark_all_notifications_read` | none | `list[NotificationResponse]` | yes | owner | mark all read | optional |
| GET/PATCH/POST | `/api/v1/notification-settings`, `/test-email` | `notification_settings.py` | settings functions | settings schemas | settings/test response | yes | User/Admin scoped | email notification preferences | optional |
| GET | `/api/v1/admin/users` | `admin.py` | `list_users` | query | `list[AdminUserResponse]` | yes | Admin | view users | yes |
| GET | `/api/v1/admin/sensors` | `admin.py` | `list_sensors` | query | `list[AdminSensorResponse]` | yes | Admin | view sensors | yes |
| GET | `/api/v1/admin/plants` | `admin.py` | `list_plants` | query | `list[AdminPlantResponse]` | yes | Admin | view plants | yes |
| GET | `/api/v1/admin/alerts` | `admin.py` | `list_alerts` | query | `list[AdminAlertResponse]` | yes | Admin | view alerts | yes |
| GET | `/api/v1/admin/logs` | `admin.py` | `list_logs` | query | `list[SystemLogResponse]` | yes | Admin | view system logs | yes |
| GET | `/api/v1/stream/alerts` | `stream.py` | `stream_alerts` | none | SSE | yes | User/Admin scoped | alert stream | yes |
| GET | `/api/v1/stream/notifications` | `stream.py` | `stream_notifications` | none | SSE | yes | User/Admin scoped | notification stream | optional |
| GET | `/api/v1/stream/dashboard/{plant_id}` | `stream.py` | `stream_dashboard` | none | SSE | yes | owner/Admin | dashboard updates | yes |
| GET | `/health` | `main.py` | `healthcheck` | none | JSON | no | None | service health | yes |

Standalone AI/classification endpoint: Not found in the repository. Recommendations are embedded in dashboard/alerts and generated in services, not exposed as a separate recommendation endpoint. Plant type endpoints are implemented as `plant-care-profiles`, not a traditional `plant_types` CRUD table. User management beyond `/auth/me` is admin read-only list; admins cannot edit/deactivate users in current code.

## 5. Authentication and Authorization Verification

| user auth feature | implemented / partial / not found | file evidence | safe thesis wording |
|---|---|---|---|
| registration workflow | implemented | `AuthService.register`, `/auth/register` | users can register accounts |
| login workflow | implemented | `AuthService.login`, `/auth/login` | users authenticate by email/password |
| password hashing | implemented | `hash_password` uses bcrypt | passwords are stored as bcrypt hashes |
| JWT creation | implemented | `create_access_token` | JWT access tokens are issued |
| JWT expiration | implemented | `exp`, `ACCESS_TOKEN_EXPIRE_MINUTES=60` | access tokens have configured expiration |
| refresh tokens | not found | no session/token table or endpoint | do not claim refresh-token support |
| logout | partially implemented | frontend removes token from localStorage | client-side logout only |
| current user dependency | implemented | `get_current_user` | protected endpoints resolve active user |
| admin dependency | implemented | `require_admin` | admin routes require Admin role |
| User role | implemented | `UserRole.USER` | User role exists |
| Admin role | implemented | `UserRole.ADMIN` | Admin role exists |
| inactive user behavior | implemented | query filters `User.is_active.is_(True)` | inactive users cannot authenticate via token dependency |
| frontend token storage | implemented | `localStorage` key `smart-plant-token` | browser stores JWT in localStorage |
| protected frontend routes | implemented | `ProtectedLayout` | frontend routes require token/user state |
| role-based frontend rendering | partial | admin link/page guarded by role | admin UI is conditionally shown |

| device auth feature | implemented / partial / not found | file evidence | safe thesis wording |
|---|---|---|---|
| sensor device token generation | implemented | `generate_device_token`, `SensorService.create` | admin provisioning creates one-time token |
| token hashing | implemented | `hash_device_token` using bcrypt | device tokens stored as hashes |
| token verification | implemented | `verify_device_token`, `AlertService.ingest_sensor_data` | ingestion verifies token |
| `X-Device-Token` header | implemented | `ingest.py`, gateway `send_reading` | gateway sends token header |
| `device_id` path parameter | implemented | `/ingest/sensors/{device_id}/data` | sensor identified by backend device id |
| token rotation | implemented | `/sensors/{sensor_id}/rotate-token` | admins can rotate device tokens |
| invalid token behavior | implemented | 401, sensor error, system log | invalid tokens are rejected and logged |

## 6. Database Design Verification

Actual tables: `users`, `plants`, `plant_care_profiles`, `sensors`, `sensor_data`, `alerts`, `alert_transitions`, `recommendations`, `notifications`, `user_notification_settings`, `system_logs`.

| table name | model class | primary key | fields / data types / constraints | relationships / indexes | purpose | evidence file |
|---|---|---|---|---|---|---|
| `users` | `User` | `id` | `full_name`, unique indexed `email`, `password_hash`, enum `role`, `is_active`, timestamps | owns plants, alerts, notifications; email index | accounts | `models.py`, migration `0001` |
| `plants` | `Plant` | `id` | `user_id` FK, `name`, `species`, `location`, `description`, `image_url`, `is_active`, `deleted_at`, timestamps | user index; sensors/alerts/recommendations/notifications | plant profiles, soft delete | `models.py` |
| `plant_care_profiles` | `PlantCareProfile` | `id` | unique `slug`, unique `canonical_species`, JSON `display_names`, `thresholds`, `basic_care`, `gardener_advice`, `issues`, `stable_advice`, `is_active` | slug/species indexes | seeded care profile data | migrations `0006`, `0007`, model |
| `sensors` | `Sensor` | `id` | nullable `user_id` FK, unique indexed `device_id`, `device_token_hash`, enum `type`, enum `status`, nullable `plant_id`, `is_active`, last seen/source/error, timestamps | user/device/plant indexes | provisioned sensor devices | `models.py`, migrations |
| `sensor_data` | `SensorData` | `id` | `sensor_id` FK, `plant_id` FK, nullable floats `moisture`, `temperature`, `humidity`, `light`, indexed `recorded_at`, `created_at` | `ix_sensor_data_sensor_recorded` | environmental readings | `models.py` |
| `alerts` | `Alert` | `id` | `user_id`, `plant_id`, nullable `sensor_id`, enum `status`, enum `severity`, `title`, `message`, `metric`, `value`, `threshold`, `resolved_at`, timestamps | user/status/created index | threshold alerts | `models.py`, `AlertRepository` |
| `alert_transitions` | `AlertTransition` | `id` | `alert_id`, enum `from_status`, enum `to_status`, `changed_by`, `note`, `changed_at` | alert index | alert lifecycle history | `models.py` |
| `recommendations` | `Recommendation` | `id` | `plant_id`, nullable `alert_id`, `text`, `reason`, `is_active`, timestamps | plant index | stored alert recommendations | `models.py` |
| `notifications` | `Notification` | `id` | `user_id`, enum `type`, enum `severity`, title/message keys and text, JSON params, related plant/alert/sensor, `dedupe_key`, `read_at`, `created_at` | user/read/dedupe indexes | in-app notifications | `models.py`, migration `0003` |
| `user_notification_settings` | `UserNotificationSettings` | `id` | unique `user_id`, email, booleans for email categories, `verified_at`, timestamps | unique user | notification preferences | migrations `0004`, `0005` |
| `system_logs` | `SystemLog` | `id` | nullable `user_id`, indexed `event_type`, `message`, JSON `payload`, indexed `created_at` | event/date indexes | audit trace | `models.py` |

Answers: no separate `roles` table; no separate `plant_types` table, but `plant_care_profiles` exists; no separate `sensor_types` table; no separate `alert_types` table; no `plant_conditions` table; no refresh token/session table. Enum fields: `users.role`, `sensors.type`, `sensors.status`, `alerts.status`, `alerts.severity`, `alert_transitions.from_status`, `alert_transitions.to_status`, `notifications.type`, `notifications.severity`. Soft-deleted records: plants via `is_active=false` and `deleted_at`; users and sensors have `is_active` but no user/sensor delete endpoint found. Essential ERD: User-Plant, User-Sensor, Plant-Sensor, Sensor-SensorData, Plant-SensorData, Plant/User/Sensor-Alert, Alert-AlertTransition, Plant/Alert-Recommendation, User/Plant/Alert/Sensor-Notification, User-SystemLog, User-NotificationSettings. Appendix ERD should add `plant_care_profiles` as a lookup/display profile table not directly FK-linked.

## 7. Database Wording Check for Thesis

| statement | true / false / partially true | evidence | corrected wording if needed |
|---|---|---|---|
| The users table stores account data. | true | `User` model | keep |
| Passwords are stored as hashes. | true | `password_hash`, bcrypt | keep |
| Role is stored as enum, not a separate table. | true | `User.role`, no roles model | keep |
| Plants belong to users. | true | `Plant.user_id` | keep |
| Sensor devices can be assigned to users and attached to plants. | true | `Sensor.user_id`, `plant_id`, service methods | keep |
| Sensor readings are stored in sensor_data. | true | `SensorData` | keep |
| Alerts have statuses and severities. | true | `AlertStatus`, `AlertSeverity` | keep |
| Alert lifecycle history is stored in alert_transitions. | true | `AlertTransition` | keep |
| Recommendations are stored and can be active/inactive. | true | `Recommendation.is_active` | keep |
| Notifications are stored with read/unread status. | true | `Notification.read_at` | keep |
| System logs are stored for traceability. | partially true | selected events only | “selected system events are stored for traceability” |
| Plant condition is computed on request, not stored in a separate table. | true | `PlantConditionService`, no table | keep |
| Plant type thresholds are stored in backend plant knowledge code, not in a plant_types table. | partially true | `plant_knowledge/profiles.py`; also `plant_care_profiles.thresholds` JSON | “threshold logic is implemented in backend plant-profile code; care profile data is also seeded in `plant_care_profiles`, not `plant_types`” |

## 8. IoT Hardware and Gateway Verification

| IoT/gateway feature | implemented / partial / not found | file evidence | exact values, if found | safe thesis wording |
|---|---|---|---|---|
| Arduino firmware file | implemented | `iot/arduino_uno_sensor_node/arduino_uno_sensor_node.ino` | `.ino` sketch | Arduino Uno sketch |
| board type | implemented | gateway README | “Board: Arduino Uno” | USB-connected Arduino Uno |
| sensors used/assumed | implemented | firmware includes `SoilMoisture`, `DHT`, `LDR` | DHT11 default, soil analog, LDR | low-cost environmental sensors |
| measured parameters | implemented | firmware JSON fields | soil, humidity, temperature, light | four environmental parameters |
| serial format | implemented | `Serial.print` JSON | JSON line | JSON-formatted serial data |
| baud rate | implemented | `SERIAL_BAUD_RATE=9600` | 9600 | keep |
| reading interval | implemented | `READ_INTERVAL_MS=5000` | 5 seconds | periodic readings |
| raw field names | implemented | firmware | `soil_raw`, `humidity`, `temperature`, `light_raw` | keep |
| gateway CLI | implemented | `build_parser` | port, baud, backend-url, device-id, token, interval, calibration | configurable Python gateway |
| invalid JSON handling | implemented | `parse_json_line` warning/skip | skipped | safe |
| missing values | partial | humidity/temp nullable; soil/light required | DHT can be null; raw soil/light required | partial missing-value handling |
| soil conversion | implemented | `normalize_reading` | default 0 wet, 220 dry -> 0..100% | normalized soil moisture percentage |
| light conversion | implemented | `light_raw / 1023 * 1000` | 0..1000 score | normalized light score, not lux |
| backend payload | implemented | `send_reading` | `moisture`, `temperature`, `humidity`, `light` | keep |
| headers | implemented | gateway and ingest | `X-Device-Token`, `X-Ingest-Source` | keep |
| retry behavior | implemented | loop sleeps after failed send | `retry_delay` default 5 | basic retry loop |
| logging | implemented | Python logging | accepted/error messages | gateway logs operational status |

Actual data flow: Arduino Uno reads analog/DHT values -> prints JSON over USB serial -> Python gateway parses and normalizes -> POSTs to FastAPI ingest endpoint with device token -> backend stores `sensor_data`, evaluates thresholds, creates alerts/recommendations/notifications, publishes SSE -> frontend updates dashboard.

Raw JSON example: `{"soil_raw":40,"humidity":36.5,"temperature":27.1,"light_raw":120}`. Normalized JSON example: `{"moisture":81.8,"temperature":27.1,"humidity":56.5,"light":117.3}`. Backend request: `POST /api/v1/ingest/sensors/arduino-uno-001/data` with `X-Device-Token: <SECRET>` and JSON body. Light is a normalized project score, not lux. This is USB/serial, not wireless.

## 9. Sensor Data Model and Validation Verification

| parameter | field name in Arduino raw JSON | field name in gateway normalized payload | backend schema field | database column | unit | range/validation | where validation occurs | what happens if missing |
|---|---|---|---|---|---|---|---|---|
| soil moisture | `soil_raw` | `moisture` | `moisture` | `sensor_data.moisture` | percent | gateway clamps 0..100 | gateway | raw missing rejects; backend accepts null if payload has null |
| air temperature | `temperature` | `temperature` | `temperature` | `sensor_data.temperature` | Celsius | finite or null in gateway; no backend range | gateway only | stored null |
| air humidity | `humidity` | `humidity` | `humidity` | `sensor_data.humidity` | percent | offset then clamp 0..100 | gateway | stored null |
| light intensity | `light_raw` | `light` | `light` | `sensor_data.light` | normalized score 0..1000 | gateway clamps raw and score | gateway | raw missing rejects; backend accepts null if payload has null |

Backend Pydantic schema uses optional floats and does not enforce physical ranges. Gateway validates finite numeric raw soil/light values, optional finite temperature/humidity, clamps soil/light/humidity, and skips invalid readings. Chapter 3 should say validation and normalization are primarily performed in the serial gateway, while backend ingestion accepts nullable numeric fields and stores timestamps.

## 10. Plant Knowledge and Rule-Based Logic Verification

| plant profile | species/canonical name | supported / fallback | threshold fields | evidence |
|---|---|---|---|---|
| common tropical aroid vine profile | `Epipremnum aureum` | default/fallback | moisture, temperature, humidity, light min/max/optimal | `profiles.py` |
| Heartleaf philodendron | `Philodendron hederaceum` | supported alias but same thresholds | same shared thresholds | `SUPPORTED_SPECIES`, migration `0007` |
| Satin pothos | `Scindapsus pictus` | supported alias but same thresholds | same shared thresholds | migration `0007` |
| Arrowhead vine | `Syngonium podophyllum` | supported alias but same thresholds | same shared thresholds | migration `0007` |

| parameter | min | max | optimal range | issue below | issue above | recommendation text | evidence |
|---|---:|---:|---|---|---|---|---|
| moisture | 35 | 75 | 45-65 | `low_moisture` | `high_moisture` | water gradually / pause watering | `profiles.py` |
| temperature | 18 | 30 | 20-27 | `low_temperature` | `high_temperature` in code | move warmer/cooler | `profiles.py` |
| humidity | 40 | 80 | 50-70 | `low_humidity` | no high-humidity issue in profile code | increase humidity | `profiles.py` |
| light | 40 | 320 | 45-180 | `low_light` | no high-light alert issue in profile code | move to brighter indirect light | `profiles.py` |

| rule-based condition output | condition/status | score rule | risk factors | evidence |
|---|---|---|---|---|
| no current data | `insufficient_data` | `health_score=None` | none | `PlantConditionService.evaluate` |
| normal | `normal` | score >= 75 and no risks | none | service |
| attention | `attention` | score < 75 or risks | issue codes/trends | service |
| critical | `critical` | score < 50 or penalty >= 40 | severe issue codes | service |

The system is no longer only Golden pothos in UI/profile rows, but thresholds are effectively shared aroid-vine thresholds based on the Golden pothos/common profile. Thresholds are partly hardcoded in `plant_knowledge/profiles.py` and also seeded to `plant_care_profiles`; condition logic uses code profiles, not user-configurable database editing. “Plant-profile thresholds” is accurate. “Plant type table” is inaccurate; use “plant care profile table” only if describing `plant_care_profiles`.

## 11. Alert Logic and Lifecycle Verification

| alert feature | implemented / partial / not found | evidence | safe thesis wording |
|---|---|---|---|
| alert table/model | implemented | `Alert` model | alerts are persisted |
| statuses | implemented | created/viewed/acknowledged/resolved/closed | alert lifecycle statuses |
| severities | implemented | low/medium/high/critical | severity levels |
| creation conditions | implemented | `_profile_checks` | created on profile threshold violations |
| deduplication | implemented | `find_open_by_metric_direction` | open duplicate alerts are skipped |
| existing alerts updated | not found | existing alert causes `continue` | not updated; duplicate creation avoided |
| auto-resolve | not found | no logic when values normalize | do not claim auto-resolution |
| who transitions | implemented scoped owner | `AlertWorkflowService.get_for_user` | users transition their own alerts |
| admins transition any alert | not found | admin endpoint list only | do not claim admin transition |
| transition history | implemented | `alert_transitions` | lifecycle history stored |
| notifications from alerts | implemented | `NotificationService.create_for_alert` | alerts create notifications |
| recommendations from alerts | implemented | `RecommendationService.create_for_alert` | alerts create recommendations |
| SSE events | implemented | event_bus publish alerts | new/transition events streamed |

| from status | allowed to status | evidence | should be shown in lifecycle diagram |
|---|---|---|---|
| created | viewed, acknowledged, resolved | `ALLOWED_TRANSITIONS` | yes |
| viewed | acknowledged, resolved | same | yes |
| acknowledged | resolved | same | yes |
| resolved | closed | same | yes |
| closed | none | same | yes |

| threshold issue | metric | alert title/message pattern | severity calculation | recommendation created | evidence |
|---|---|---|---|---|---|
| low_moisture | moisture | profile localized title/message, English selected | ratio threshold/value | yes | `AlertService`, `profiles.py` |
| high_moisture | moisture | profile title/message | value/threshold, sustained 48h/3 samples required | yes | `AlertService` |
| low_temperature | temperature | profile title/message | threshold/value | yes | code |
| high_temperature | temperature | profile title/message | value/threshold | yes | code |
| low_humidity | humidity | profile title/message | threshold/value | yes | code |
| low_light | light | profile title/message, skipped at night | threshold/value | yes | code |

Lifecycle diagram text: `Created -> Viewed -> Acknowledged -> Resolved -> Closed`. Direct transitions also implemented: `Created -> Acknowledged`, `Created -> Resolved`, `Viewed -> Resolved`.

## 12. Recommendation Module Verification

| triggering condition | metric | recommendation text | source: rule-based / AI-supported / hybrid | stored in DB | related to alert | evidence |
|---|---|---|---|---|---|---|
| low moisture | moisture | water gradually and re-check | rule-based | yes for alert; dashboard current is computed | yes when alert-triggered | `profiles.py`, `RecommendationService` |
| high moisture | moisture | pause watering/dry soil | rule-based | yes | yes | same |
| low/high temperature | temperature | move warmer/cooler | rule-based | yes | yes | same |
| low humidity | humidity | increase ambient humidity | rule-based | yes | yes | same |
| low light | light | move to brighter indirect light | rule-based | yes | yes | same |
| stable condition | stable | keep current routine | rule-based | not necessarily; dashboard summary computed | no | `build_current_recommendation` |

It is not safe to say “AI recommendation module” if that implies ML generates text. Use: “rule-based recommendation module with AI-supported plant condition classification.” ML supports status classification in dashboard condition, while recommendation text comes from plant-profile rules.

## 13. AI/ML Module Verification

| AI/ML component | actual implementation | file evidence | safe thesis wording |
|---|---|---|---|
| model type | `RandomForestClassifier` | `train_condition_model.py`, metadata | Random Forest classifier |
| library | scikit-learn | imports and requirements | machine learning module |
| training script | implemented | `train_condition_model.py` | training script included |
| dataset | synthetic/generated CSV | `training_dataset.csv`, generator functions | synthetic project dataset |
| dataset size | 420 rows | metadata, CSV line count 421 incl. header | 420 samples |
| labels | normal, attention, critical | `LABELS`, metadata | condition classes |
| train/test split | 25% test, stratified | `train_test_split(test_size=0.25)` | keep |
| features | 8 environmental/trend fields | `FEATURE_COLUMNS` | current readings plus trends |
| metrics saved | accuracy only | `model_metadata.json` | accuracy can be reported with limitation |
| classification report | printed, not saved | script prints `classification_report` | do not report unless rerun and capture |
| artifact path | `app/ml/plant_condition_model.joblib` | file exists | keep |
| metadata path | `app/ml/model_metadata.json` | file exists | keep |
| loading | joblib load in service | `MLConditionService` | loaded at runtime |
| prediction called | dashboard condition evaluation | `PlantConditionService._predict_ml` | supports dashboard assessment |
| fallback | returns no ML result if unavailable/error/missing values | `_safe_result` | rule-based baseline remains primary |
| probabilities | implemented | `predict_proba`, `class_probabilities` | confidence/probability shown |
| confusion matrix | not found | no file/code | do not claim |
| real sensor training | not found | generator uses random synthetic rows | do not claim |
| agronomic validation | not found | no validation docs/data | do not claim |

| feature name | source | current reading or trend | required for prediction | evidence |
|---|---|---|---|---|
| moisture | dashboard current | current | yes | `_build_ml_features` |
| temperature | dashboard current | current | yes | same |
| humidity | dashboard current | current | yes | same |
| light | dashboard current | current | yes | same |
| moisture_trend | history delta | trend | yes, defaults 0 if insufficient history | same |
| temperature_trend | history delta | trend | yes | same |
| humidity_trend | history delta | trend | yes | same |
| light_trend | history delta | trend | yes | same |

| model output class | meaning in application | evidence |
|---|---|---|
| `normal` | supporting prediction of normal condition | `LABELS`, dashboard schema |
| `attention` | supporting prediction that plant needs attention | same |
| `critical` | supporting prediction of critical condition | same |

Answers: “AI-supported classification” is accurate. “Diagnosis” is inaccurate/risky. “Deep learning” is inaccurate. “Random Forest classifier” is accurate. “Trained on synthetic data generated in project code” is accurate. Accuracy can be reported only as synthetic test accuracy: `1.0` in `model_metadata.json`; explain limitation. Precision/recall/F1 are printed but not saved, so include only if rerun and documented. Real agronomic validation: Not found in the repository.

## 14. Frontend Verification

| frontend feature | implemented / partial / not found | file evidence | safe thesis wording |
|---|---|---|---|
| React | implemented | package and `.tsx` | React frontend |
| TypeScript | implemented | `.tsx`, `tsconfig.json` | TypeScript |
| routing | implemented | `router.tsx` | client routing |
| protected routes | implemented | `ProtectedLayout` | protected dashboard routes |
| auth state | implemented | `AppStateContext` | global auth state |
| token storage | implemented | localStorage | JWT stored client-side |
| API client | implemented | `api.ts` | central API layer |
| dashboard page | implemented | `DashboardPage`, `Dashboard` | plant monitoring overview |
| plant list/details | implemented | `PlantsIndexPage`, `PlantDetailsPage` | plant views |
| analytics | implemented | `AnalyticsPage`, `Analytics` | historical charts and CSV export |
| alerts | implemented | `AlertsPage`, `Alerts` | alert list/lifecycle controls |
| notifications | implemented | `NotificationsPanel` | in-app notifications |
| settings/sensors | implemented read-only for users | `SettingsPage`, `Sensors readOnly` | users view assigned sensors |
| admin page | implemented | `AdminPage` | admin monitoring/provisioning |
| charting | implemented | Recharts | line/area charts |
| CSV export | implemented | `Analytics.exportCsv` | export historical data |
| photo upload | implemented | `uploadPlantPhoto`, `PlantDetails` | plant photo upload |
| SSE handling | implemented | fetch-event-source | alerts, notifications, plant dashboard |
| manual refresh | implemented | dashboard/details/admin/alerts | refresh buttons |
| search/sort | implemented | `Dashboard` | plant filtering/sorting |
| role-based UI | partial | admin link/page redirect | frontend role-aware UI |
| i18n | implemented | `i18n.tsx` | kk/ru/en language support |
| frontend tests | not found | no test script/files | do not claim automated frontend tests |
| build scripts | implemented | `npm run build` | build verified |

| page/component | file path | purpose | API endpoints used | role access | screenshot recommended |
|---|---|---|---|---|---|
| Dashboard | `src/pages/DashboardPage.tsx`, `components/Dashboard.tsx` | plant overview | plants, dashboard, plant-care-profiles | User/Admin | yes |
| Plant details | `src/pages/PlantDetailsPage.tsx` | latest readings, charts, recommendation, photo | plant, dashboard, stream/dashboard, photo | owner/Admin stream | yes |
| Analytics | `src/pages/AnalyticsPage.tsx` | historical charts/CSV | dashboard | User/Admin | yes |
| Alerts | `src/pages/AlertsPage.tsx` | alert lifecycle | alerts endpoints | User/Admin scoped | yes |
| Admin | `src/pages/AdminPage.tsx` | users/sensors/plants/alerts/logs, sensor provisioning | admin and sensor endpoints | Admin | yes |
| Notifications | `components/NotificationsPanel.tsx` | notification menu | notifications, SSE | User/Admin scoped | optional |
| Profile | `src/pages/ProfilePage.tsx` | user info and email prefs | notification-settings | User/Admin | optional |
| Settings/Sensors | `src/pages/SettingsPage.tsx`, `components/Sensors.tsx` | read-only user sensor status | sensors | User/Admin scoped | optional |

## 15. Dashboard and Data Visualization Verification

Backend data flow: `GET /dashboard/plants/{plant_id}` -> `MonitoringService.get_dashboard` -> verify plant owner -> latest/history from `SensorDataRepository` -> `PlantConditionService.evaluate` -> `MLConditionService.predict_condition` if possible -> rule-based recommendation summary -> response.

Frontend data flow: route/page loads plants -> calls dashboard snapshots per plant or detail dashboard -> renders metric cards and Recharts history -> subscribes to SSE for detail dashboard and refreshes on sensor events.

| dashboard field | source |
|---|---|
| `plant_id` | request path |
| `last_updated_at` | latest `sensor_data.recorded_at` |
| `current` | latest sensor row |
| `history` | sensor rows in `hours` window |
| `condition` | computed by `PlantConditionService` |
| `ml_prediction`, `ml_confidence`, probabilities | Random Forest service when all four current values exist |
| `active_recommendation` | rule-based current recommendation |
| `care_profile` | DB `plant_care_profiles` if found |
| `today_care` | computed care actions |

“Near real-time” is accurate because SSE triggers refresh after ingestion events. “Real-time” alone is too strong. Use “near real-time updates using Server-Sent Events.” Chart data is stored sensor history with frontend mapping; condition and recommendation are processed/computed.

## 16. Admin Monitoring Verification

| admin function | implemented / partial / not found | evidence | safe thesis wording |
|---|---|---|---|
| user list | implemented | `/admin/users`, AdminPage | admins can view users |
| sensor list | implemented | `/admin/sensors`, AdminPage | admins can view sensors |
| alert list | implemented | `/admin/alerts` | admins can view alerts |
| log list | implemented | `/admin/logs` | admins can view logs |
| plant list | implemented | `/admin/plants` | admins can view active plants |
| sensor provisioning | implemented | `POST /sensors` admin | admins provision sensors |
| sensor assignment | implemented | `/sensors/{id}/assign` | admins assign sensors |
| sensor attach/detach | implemented | attach/detach endpoints | admins attach/detach sensors |
| token rotation | implemented | rotate-token endpoint | admins rotate device tokens |
| user editing/deactivation | not found | no endpoint/service | do not claim |
| alert transition as admin for any user | not found | user-scoped transition only | do not claim |
| plant management as admin | partial/not found | list only | admins view plants, not manage all plants |
| role restrictions | implemented | `require_admin`, frontend redirect | backend admin enforcement |

Admin can view users/sensors/plants/alerts/logs and provision/assign/attach/detach/rotate sensors. Do not claim full user management, full plant management, or global alert lifecycle management.

## 17. Logging and Audit Verification

| event | logged in system_logs | where logged | payload fields | visible to admin | safe thesis wording |
|---|---|---|---|---|---|
| registration | yes | `AuthService.register` | none | yes | selected auth events logged |
| login | yes | `AuthService.login` | none | yes | successful login logged |
| failed login | no | Not found in the repository. | n/a | no | do not claim |
| plant created | yes | `PlantService.create` | `plant_id` | yes | selected plant events logged |
| plant updated | no | Not found in the repository. | n/a | no | do not claim |
| plant deleted | yes | `PlantService.delete` | `plant_id` | yes | soft delete logged |
| sensor registered | yes | `SensorService.create` | `sensor_id` | yes | sensor provisioning logged |
| sensor assigned | yes | `SensorService.assign` | sensor/user | yes | keep |
| sensor attached | yes | `SensorService.attach` | sensor/plant/user | yes | keep |
| sensor detached | yes | `SensorService.detach` | sensor/user | yes | keep |
| sensor token rotated | yes | `SensorService.rotate_token` | `sensor_id` | yes | keep |
| sensor reading received | no persistent log | data stored in `sensor_data` | n/a | via data not logs | do not say each reading is audit-logged |
| invalid sensor reading | no system log | gateway logs warning; backend validation error | n/a | no | gateway logs invalid readings |
| ingest auth failed | yes | `AlertService.ingest_sensor_data` | sensor/source | yes | invalid device auth logged |
| alert created | yes | `AlertService._evaluate_thresholds` | alert/metric/issue/value | yes | keep |
| alert transitioned | yes | `AlertWorkflowService.transition` | alert/from/to | yes | keep |
| recommendation generated | no direct log | stored in `recommendations` | n/a | via recommendation table | do not claim log |
| notification generated | no system log | stored in `notifications` | n/a | via notification table | do not claim log |
| admin action | partial | sensor actions use admin user id | action-specific | yes | selected admin actions logged |

## 18. Testing Verification

| test category | file path | what is tested | command to run | current status if known | should be mentioned in thesis |
|---|---|---|---|---|---|
| backend auth/security | `practice-backend/tests/test_security.py` | password/JWT/device token hashing | `.venv\Scripts\python -m pytest -q` | 53 passed total | yes |
| backend alerts | `test_alert_fsm.py`, `test_alert_dedup.py` | lifecycle/dedup | same | passed | yes |
| backend notifications | notification tests | notification settings/creation | same | passed | yes |
| backend plant logic | `test_plant_condition.py`, `test_plant_knowledge.py`, `test_ml_condition_service.py` | rules and ML fallback | same | passed | yes |
| backend sensors | `test_sensor_lifecycle.py` | admin provisioning and gateway ingest | same | passed | yes |
| gateway unit tests | `iot/serial_gateway/tests/test_serial_gateway.py` | parsing/normalization/url | `.venv\Scripts\python -m pytest -q` after installing pytest | not run; pytest missing in gateway venv | yes with caveat |
| frontend build | `smart-plant-frontend` | TypeScript and Vite build | `npm run build` | passed; large chunk warning | yes |
| frontend automated tests | Not found in the repository. | n/a | n/a | not found | no |
| API smoke tests | `practice-backend/http/smoke-test.http` | manual API flow | HTTP client | present, not executed here | optional |
| CI/CD | Not found in the repository. | n/a | n/a | not found | no |
| Swagger/OpenAPI | FastAPI automatic docs | API docs | `/docs` while backend runs | available by framework | yes screenshot |

Backend automated tests are present and pass: `53 passed in 8.88s`. Frontend automated tests are not found. Gateway tests are present but current gateway venv lacks pytest; global run also missed `httpx`. Test count should be documented as 53 backend tests plus gateway tests present but not currently executed unless dependencies are installed. Thesis should say “testing was performed for backend services, frontend build, and gateway parsing logic” rather than blanket “all tests passed” unless gateway tests are rerun. Recommended screenshots: backend pytest pass, frontend build, Swagger docs, gateway terminal accepted payload.

## 19. Deployment and Configuration Verification

| configuration/deployment feature | implemented / partial / not found | evidence | safe thesis wording |
|---|---|---|---|
| backend env example | implemented | `.env.example` | configurable local backend |
| frontend env usage | implemented | `VITE_API_BASE_URL` in `api.ts` | frontend API base configurable |
| gateway CLI args | implemented | `build_parser` | gateway configured by CLI |
| docker-compose database | implemented | PostgreSQL service | local PostgreSQL via Docker Compose |
| backend Dockerfile | partial/not useful | `practice-backend/Dockerfile` is empty | do not claim backend container image |
| frontend Dockerfile | not found | Not found in the repository. | do not claim |
| cloud deployment | not found | Not found in the repository. | do not claim |
| AI model path config | partial | fixed paths in `app/ml/__init__.py` | model artifact stored in backend app path |
| CORS config | implemented | `CORS_ORIGINS` | CORS configurable |
| secret keys | implemented | `.env.example` has sample | use `<SECRET>` in thesis |
| admin bootstrap | implemented | `ADMIN_EMAIL`, `ADMIN_PASSWORD` in lifespan | optional admin bootstrap |

Startup commands: backend `cd practice-backend; .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`; frontend `cd smart-plant-frontend; npm run dev -- --host 127.0.0.1 --port 5173`; database `cd practice-backend; docker compose up -d`; gateway `cd iot\serial_gateway; .\.venv\Scripts\python serial_gateway.py --port COM3 --backend-url http://127.0.0.1:8000 --device-id arduino-uno-001 --device-token <SECRET> --source-label serial:COM3`; migrations `cd practice-backend; .\.venv\Scripts\alembic upgrade head`.

## 20. Chapter 3 Statement Accuracy Check

| statement | status | evidence | corrected wording for thesis |
|---|---|---|---|
| 1. Functional web application for plant condition monitoring. | accurate | backend/frontend/gateway | keep |
| 2. Monitors soil moisture, air temperature, air humidity, light intensity. | accurate | firmware, schema | keep; light is score |
| 3. Uses USB-connected Arduino Uno sensor node. | accurate | Arduino README/sketch | keep |
| 4. Python gateway reads JSON-formatted serial data. | accurate | `serial_gateway.py` | keep |
| 5. Gateway normalizes soil moisture and light values. | accurate | `normalize_reading` | keep |
| 6. Light intensity is stored as lux. | inaccurate | README says not lux | “stored as normalized light score” |
| 7. Backend uses FastAPI. | accurate | requirements/main | keep |
| 8. PostgreSQL persistent storage. | accurate | Docker Compose/SQLAlchemy | keep |
| 9. Backend follows layered architecture. | accurate | folders/services/repos | keep |
| 10. Frontend React and TypeScript. | accurate | package | keep |
| 11. Frontend uses SSE for selected updates. | accurate | fetch-event-source | keep |
| 12. JWT authentication for users. | accurate | security.py | keep |
| 13. bcrypt password hashing. | accurate | security.py | keep |
| 14. Sensor ingestion uses X-Device-Token. | accurate | ingest/gateway | keep |
| 15. User and Admin roles. | accurate | enum | keep |
| 16. Admins can provision and assign sensors. | accurate | sensor/admin UI | keep |
| 17. Admins can fully manage users. | inaccurate | list only | “admins can view users” |
| 18. Users can create plant profiles. | accurate | `/plants` | keep |
| 19. Users can view historical charts. | accurate | Analytics/PlantDetails | keep |
| 20. Alerts have a lifecycle. | accurate | FSM | keep |
| 21. Alerts auto-resolve when values return normal. | inaccurate | Not found | remove |
| 22. Recommendations are generated by ML. | inaccurate | RecommendationService rules | “rule-based recommendations” |
| 23. Recommendations are rule-based. | accurate | profiles/service | keep |
| 24. AI module uses Random Forest. | accurate | metadata/script | keep |
| 25. AI module uses deep learning. | inaccurate | scikit RF only | remove |
| 26. AI output is final diagnosis. | inaccurate | rule primary | “supporting classification” |
| 27. AI output is supporting classification. | accurate | explanation text | keep |
| 28. Model trained on synthetic data. | accurate | generator/metadata | keep with limitation |
| 29. Model trained on real-world agronomic data. | inaccurate | Not found | remove |
| 30. System controls irrigation. | inaccurate | Not found | remove |
| 31. System controls actuators. | inaccurate | Not found | remove |
| 32. Implements wireless sensor network. | inaccurate | USB serial | remove |
| 33. Provides administrative logs. | accurate | `/admin/logs` | keep, selected logs |
| 34. Production-grade secure. | needs cautious wording | local demo env, localStorage JWT, no refresh | “basic security mechanisms for prototype” |
| 35. Real-world agronomic validation. | inaccurate | Not found | remove |

## 21. Diagrams, Tables, and Screenshots Checklist

| item number | type | recommended title | source to create it from | Chapter 3 section | required / optional | what it proves |
|---:|---|---|---|---|---|---|
| 1 | diagram | General System Architecture | README data flow and folders | architecture | required | web app scope |
| 2 | diagram | Client-Side Architecture | `src/router.tsx`, `AppStateContext` | frontend | required | routing/state/API |
| 3 | diagram | Server-Side Layered Architecture | backend folders | backend | required | layered backend |
| 4 | diagram | IoT Data Flow | Arduino/gateway/ingest | IoT | required | USB serial path |
| 5 | diagram | AI-Supported Analysis Flow | `PlantConditionService`, ML service | AI | required | rule primary, ML support |
| 6 | diagram | Simplified ERD | essential ERD list | database | required | core relations |
| 7 | diagram | Full ERD | all tables | appendix | optional/appendix | complete schema |
| 8 | diagram | Customer Journey Map | frontend routes | validation | optional | user/admin workflow |
| 9 | table | API Endpoint Groups | router extraction | backend API | required | real endpoints |
| 10 | table | Database Tables | ORM models | database | required | schema evidence |
| 11 | table | User Stories and Acceptance Criteria | README/docs/tests | validation | required | implemented flows |
| 12 | diagram | Alert Lifecycle | `ALLOWED_TRANSITIONS` | alerts | required | FSM |
| 13 | screenshot | Dashboard | running frontend | frontend | required | overview UI |
| 14 | screenshot | Plant Details | running frontend | frontend | required | readings/charts/recommendation |
| 15 | screenshot | Alerts | running frontend | alerts | required | lifecycle UI |
| 16 | screenshot | Admin Panel | running frontend admin | admin | required | provisioning/logs |
| 17 | screenshot | Swagger/OpenAPI | `http://127.0.0.1:8000/docs` | API | required | documented API |
| 18 | screenshot | Backend Test Terminal | pytest output | testing | required | tests passed |
| 19 | screenshot | Gateway Terminal | accepted payload log | IoT/testing | required | end-to-end ingest |
| 20 | screenshot | Sample Database Records | pgAdmin/psql | database | optional | persistence |

## 22. Final Corrections Needed in Chapter 3

### Must fix

- Replace lux claims with normalized light score.
- Remove automated irrigation, actuator control, greenhouse automation, wireless sensor network, computer vision, plant disease diagnosis, deep learning, and real agronomic validation claims.
- Do not say recommendations are generated by ML.
- Do not say admins fully manage users.
- Do not say alerts auto-resolve.
- Do not describe `diploma practice part/` ESP32 code as current implementation.

### Should soften

- “AI” should be “AI-supported classification” or “Random Forest supporting model.”
- “Real-time” should be “near real-time using Server-Sent Events.”
- “Secure” should be “basic authentication and authorization mechanisms for a prototype.”
- “Plant types” should be “plant care profiles/shared profile thresholds.”
- “Audit logging” should be “selected system events are logged.”

### Can keep

- Developed functional smart web application.
- FastAPI + PostgreSQL + React TypeScript stack.
- USB Arduino Uno -> Python serial gateway -> backend -> database -> dashboard flow.
- JWT user authentication and bcrypt password hashing.
- Device-token sensor ingestion.
- User/Admin roles.
- Dashboard, history charts, alerts, recommendations, notifications, admin monitoring.
- Random Forest classifier trained on synthetic project dataset.

### Missing technical details to add

- Exact active directories and legacy directories.
- API endpoint group table.
- Database table/enums/indexes summary.
- Gateway calibration constants and light-score clarification.
- Alert FSM and no auto-resolve limitation.
- ML metadata: 420 synthetic rows, 8 features, 3 classes, accuracy stored as `1.0`.
- Testing evidence: 53 backend tests passed, frontend build passed, gateway tests present but require pytest dependency.

### Claims to avoid

- Disease diagnosis, computer vision, deep learning, automated irrigation, actuator control, greenhouse automation, wireless sensor network implementation, industrial agriculture automation, production-grade security, real-world agronomic validation, real lux measurement, full admin user management.

## 23. Final Safe Technical Summary

- A functional smart web application was developed for environmental plant condition monitoring.
- The implementation monitors soil moisture, air temperature, air humidity, and a normalized light score.
- The current IoT path uses a USB-connected Arduino Uno sensor node.
- Arduino firmware outputs JSON lines over serial at 9600 baud every 5 seconds.
- A Python serial gateway reads Arduino JSON, validates raw values, normalizes them, and forwards readings to the backend.
- Soil moisture is converted to a 0-100 percentage using configurable calibration values.
- Light is converted from LDR raw value to a 0-1000 project score, not lux.
- The backend is implemented with FastAPI and async SQLAlchemy.
- PostgreSQL is used as persistent storage, with Alembic migrations.
- The frontend is implemented with React and TypeScript using Vite.
- User and Admin roles are implemented using an enum field.
- JWT authentication is implemented for users, and bcrypt is used for password hashes.
- Sensor ingestion uses device-token authentication through the `X-Device-Token` header.
- Admins can provision sensors, assign sensors to users, attach/detach sensors to plants, and rotate device tokens.
- Users can create and manage plant records, upload plant photos, view dashboards, charts, alerts, and recommendations.
- The dashboard includes latest readings, historical chart data, condition assessment, and recommendation summaries.
- Server-Sent Events provide near real-time updates for alerts, notifications, and plant dashboard changes.
- Alerts are rule-based threshold alerts with statuses, severities, transition history, notifications, and stored recommendations.
- Recommendations are rule-based and derived from plant-profile issue definitions, not directly generated by ML.
- The AI/ML module is a Random Forest classifier used as supporting condition classification.
- The ML model is trained on synthetic data generated by project code, with no evidence of real-world agronomic validation.
- The system does not implement plant disease diagnosis, computer vision, deep learning, actuator control, automated irrigation, wireless sensor networking, or industrial agricultural automation.
