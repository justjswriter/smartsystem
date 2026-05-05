# План закрытия пробелов дипломного MVP Smart Plant Monitoring

## Summary

Цель: довести текущий проект до демонстрируемой дипломной версии, которая убедительно соответствует теме **IoT + AI technologies for plant condition monitoring**. Основной путь: не переписывать архитектуру, а усилить существующий FastAPI/React MVP в четырёх местах: защищённый IoT-ingest, лёгкий ML/интеллектуальный анализ состояния, полный UI для user stories, и демонстрационная/тестовая база для защиты.

Выбранный объём:
- AI: лёгкий объяснимый ML/скоринг состояния растения, без внешнего AI API.
- IoT: защищённый Device API для подготовленного Arduino/ESP/датчика.
- UI: полный UI для всех user stories, включая admin read-only панель, рекомендации, детали alert и фильтры.

## Key Changes

### 1. IoT Integration: защищённый контур датчиков

- Добавить у сенсора поля для безопасного подключения:
  - `device_token_hash`
  - `last_ip` или `last_ingest_source` как диагностическое поле
  - `last_error_at` и `last_error_message` для admin monitoring
- Изменить регистрацию сенсора:
  - пользователь/admin создаёт сенсор в UI/API;
  - backend генерирует одноразово показываемый `device_token`;
  - в БД хранится только hash токена.
- Защитить ingest:
  - `POST /api/v1/ingest/sensors/{device_id}/data` должен принимать заголовок `X-Device-Token`;
  - если токен неверный, возвращать `401`;
  - если sensor disabled/offline/deleted, возвращать понятную ошибку;
  - успешный ingest обновляет `last_seen_at`, `status=online`, пишет `sensor_data`, запускает анализ и SSE.
- Добавить endpoint для ротации токена:
  - `POST /api/v1/sensors/{sensor_id}/rotate-token`;
  - доступен владельцу растения или admin;
  - возвращает новый plain token только в ответе.
- Обновить demo:
  - `bootstrap_demo.py` должен выводить demo `device_id` и demo `device_token`;
  - `smoke-test.http` и `demo-runbook.md` должны отправлять `X-Device-Token`.

### 2. AI / Plant Condition: объяснимый интеллектуальный слой

- Добавить сущность/таблицу `plant_conditions` или расширить dashboard response вычисляемым объектом `condition`.
- Реализовать лёгкий ML-like анализ как explainable scoring:
  - вход: последние показания `moisture`, `temperature`, `humidity`, `light`, история за выбранный период;
  - выход: `condition_status`: `normal | attention | critical | insufficient_data`;
  - `health_score`: 0-100;
  - `risk_factors`: список причин, например `low_soil_moisture`, `high_temperature`;
  - `confidence`: 0-1, ниже при малом количестве данных;
  - `explanation`: короткое объяснение для UI и дипломной демонстрации.
- Назвать модуль в коде как `PlantConditionService` или аналогично, чтобы он явно отражал дипломную тему.
- Логика v1:
  - базовый scoring по отклонениям от thresholds;
  - trend factor по истории: ухудшение за последние N samples повышает риск;
  - confidence зависит от числа точек и свежести данных;
  - это можно описывать в дипломе как lightweight AI/decision-support model, не как LLM.
- Dashboard должен возвращать:
  - `current`
  - `history`
  - `condition`
  - `active_recommendation`
- Alert generation должна использовать `condition`:
  - alert создаётся при `attention/critical`, если ещё нет открытого alert по тому же metric/risk;
  - severity маппится из condition/risk.
- Recommendation должна стать частью публичного API:
  - alert detail/list возвращает хотя бы последнюю рекомендацию;
  - dashboard возвращает активную рекомендацию для растения.

### 3. Backend API completeness and security

- Закрыть текущие access gaps:
  - `POST /sensors` и `GET /sensors` требуют авторизации;
  - обычный user видит только сенсоры своих растений или unattached sensors, созданные им;
  - admin видит все.
- Добавить ownership check для SSE dashboard stream:
  - `/stream/dashboard/{plant_id}` проверяет, что растение принадлежит текущему user или user является admin.
- Доработать alert API:
  - `GET /alerts` поддерживает фильтры: `status`, `plant_id`, `severity`, `metric`;
  - `GET /alerts/{id}` возвращает transitions/history и recommendation;
  - `POST /alerts/{id}/transition` поддерживает `closed`, чтобы UI мог завершить FSM полностью.
- Доработать admin API:
  - read-only списки users/sensors/alerts/logs с query-фильтрами;
  - sensors response содержит `last_seen_at`, `status`, `plant_id`, `last_error_message`;
  - logs response фильтруется по `event_type`, `user_id`, date range.
- Audit logging:
  - писать события для sensor token rotation, ingest auth failure, sensor attach/detach, alert transitions, admin access to logs.
- Обновить Pydantic v2 warnings:
  - заменить class `Config` на `model_config = ConfigDict(from_attributes=True)` в response schemas.

### 4. Full UI for diploma user stories

- Dashboard:
  - показывать `health_score`, `condition_status`, `risk_factors`, `last_updated_at`;
  - если данных нет, показывать empty state “No sensor samples yet” и действие “Attach sensor”.
- Plant details:
  - графики для moisture, temperature, humidity, light;
  - блок “Current condition” с explanation;
  - блок “Recommendation” из API;
  - список привязанных sensors.
- Sensors/settings:
  - регистрация sensor с выбором типа;
  - показ generated device token только один раз после создания/rotation;
  - attach/detach;
  - status, last seen, disabled/offline state;
  - краткая подсказка для IoT: `device_id`, `X-Device-Token`, endpoint.
- Alerts:
  - список с фильтрами по status/severity/plant;
  - detail view alert;
  - transitions: viewed, acknowledged, resolved, closed;
  - показать recommendation и transition history.
- Admin UI:
  - отдельный route `/admin`, доступный только `role=admin`;
  - вкладки Users, Sensors, Alerts, Logs;
  - read-only таблицы, поиск/фильтр, refresh;
  - если user не admin, route скрыт и backend всё равно возвращает `403`.
- Frontend state/API:
  - обновить TypeScript types под новые response shapes;
  - использовать существующий `AppStateContext`, но вынести admin-запросы в отдельные API functions;
  - SSE alerts оставить, dashboard SSE подключить на plant details page для live updates.

## Test Plan

- Backend unit tests:
  - sensor token hashing/verification;
  - invalid/missing `X-Device-Token` rejected;
  - valid ingest creates `sensor_data` and updates sensor status;
  - plant condition scoring: normal, attention, critical, insufficient data;
  - FSM valid/invalid transitions.
- Backend integration tests:
  - user cannot list/manage another user’s sensors;
  - user cannot subscribe to another user’s dashboard SSE;
  - admin can list users/sensors/alerts/logs;
  - alert response includes recommendation and transition history.
- Frontend tests/checks:
  - `npm run build`;
  - login/register flow still compiles;
  - dashboard renders condition block with and without data;
  - alerts filters and transition buttons map to backend statuses;
  - admin route hidden for user and visible for admin.
- Demo verification:
  - update `demo-runbook.md` into a 7-10 minute сценарий:
    1. register/login user;
    2. create plant;
    3. register sensor and copy token;
    4. send IoT reading with `X-Device-Token`;
    5. show live dashboard condition;
    6. show recommendation;
    7. process alert through FSM;
    8. login admin and show sensors/logs.
  - update `smoke-test.http` so it can demonstrate the full chain without manual DB inspection.

## Assumptions

- Внешний AI API не используется: для диплома достаточно explainable lightweight ML/decision-support layer, потому что он демонстрируемый, автономный и не требует ключей.
- MQTT не добавляется в v1: подготовленное IoT-устройство будет отправлять HTTP POST на защищённый ingest endpoint.
- Admin UI делается read-only, без удаления пользователей/устройств, чтобы не расширять бизнес-риски.
- Миграции Alembic обязательны для новых полей sensor и plant condition/recommendation exposure.
- Существующая архитектура сохраняется: FastAPI routers → application services → repositories → SQLAlchemy models.
