# Acceptance Checklist by User Story (MVP)

This checklist maps each user story to implemented API endpoints, application services, and DB tables.

## US1 - Регистрация и вход пользователя

- **Endpoints**
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
- **Services**
  - `AuthService`
- **DB Tables**
  - `users`
  - `system_logs`

## US2 - Добавление и управление профилем растения

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

## US3 - Подключение и привязка IoT-сенсора к растению

- **Endpoints**
  - `POST /api/v1/sensors`
  - `GET /api/v1/sensors`
  - `POST /api/v1/sensors/{sensor_id}/attach`
  - `POST /api/v1/sensors/{sensor_id}/detach`
- **Services**
  - `SensorService`
- **DB Tables**
  - `sensors`
  - `plants`
  - `system_logs`

## US4 - Просмотр dashboard и текущего состояния растения

- **Endpoints**
  - `GET /api/v1/dashboard/plants/{plant_id}?hours=...`
- **Services**
  - `MonitoringService`
- **DB Tables**
  - `sensor_data`
  - `plants`

## US5 - Получение уведомления о критическом состоянии растения

- **Endpoints**
  - `POST /api/v1/ingest/sensors/{device_id}/data`
  - `GET /api/v1/alerts` (просмотр результата генерации)
- **Services**
  - `AlertService`
  - `RecommendationService` (triggered from alert generation)
- **DB Tables**
  - `sensor_data`
  - `alerts`
  - `alert_transitions`
  - `recommendations`
  - `system_logs`

## US6 - Просмотр AI-рекомендации (rule-based)

- **Endpoints**
  - `GET /api/v1/alerts`
  - `GET /api/v1/alerts/{alert_id}`
- **Services**
  - `RecommendationService`
  - `AlertService` (invokes recommendation generation)
- **DB Tables**
  - `recommendations`
  - `alerts`
  - `plants`

## US7 - Подтверждение и отслеживание alert (FSM)

- **Endpoints**
  - `GET /api/v1/alerts`
  - `GET /api/v1/alerts/{alert_id}`
  - `POST /api/v1/alerts/{alert_id}/transition`
- **Services**
  - `AlertWorkflowService`
- **DB Tables**
  - `alerts`
  - `alert_transitions`
  - `system_logs`

## US8 - Мониторинг устройств, пользователей и логов администратором

- **Endpoints**
  - `GET /api/v1/admin/users`
  - `GET /api/v1/admin/sensors`
  - `GET /api/v1/admin/alerts`
  - `GET /api/v1/admin/logs`
- **Services**
  - `AdminService`
- **DB Tables**
  - `users`
  - `sensors`
  - `alerts`
  - `system_logs`

## Cross-Cutting (for demo validation)

- **SSE Endpoints**
  - `GET /api/v1/stream/alerts`
  - `GET /api/v1/stream/dashboard/{plant_id}`
- **Middleware**
  - Request logging middleware (`X-Request-ID`)
  - CORS middleware
- **Config**
  - `.env` / `.env.example` for DB, security, thresholds, admin bootstrap settings
