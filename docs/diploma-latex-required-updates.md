# Required LaTeX Updates After Phase 3 and Phase 4A

This file is a draft for the teammate responsible for `diploma-latex`. Do not copy formatting blindly; adapt the text to the required thesis style.

## 1. Hardware and Data Flow

### What Is Outdated

Any reference to an ESP32-based sensor node, Wi-Fi-enabled microcontroller, direct HTTP requests from firmware, `x-api-key`, or `DEVICE_API_KEY` is outdated for the current implementation.

### Why It Is Outdated

The real hardware integration now uses Arduino Uno without Wi-Fi. Arduino prints sensor readings over USB Serial. A Python Serial Gateway reads the serial data and sends normalized telemetry to the existing FastAPI ingest endpoint using `device_id` and `X-Device-Token`.

### Replace With

Current architecture flow:

```text
Arduino Uno -> USB Serial -> Python Serial Gateway -> FastAPI -> PostgreSQL -> React frontend
```

### Replacement Paragraph

The implemented IoT data flow uses an Arduino Uno sensor node without Wi-Fi connectivity. The Arduino reads soil moisture, light, temperature, and humidity values and writes one JSON line to the USB Serial port every few seconds. A Python Serial Gateway running on the host computer reads the serial stream, normalizes raw sensor values, and forwards the existing ingest payload to the FastAPI backend using the sensor `device_id` and the `X-Device-Token` header. The backend validates the device token, stores the telemetry in PostgreSQL, updates the sensor state, evaluates the plant condition, and exposes the latest data to the React frontend.

## 2. Sensor Onboarding and Rental Provisioning Model

### What Is Outdated

Descriptions where a regular user creates a sensor, receives a device token, attaches a sensor to a plant, detaches a sensor, or rotates the token are outdated.

### Why It Is Outdated

The business model treats sensors as rented/provisioned devices. Only an administrator can manage the sensor lifecycle. Regular users can only view sensors assigned to them or attached to their own plants.

### Replacement Paragraph

Sensor onboarding is implemented as an administrator-controlled provisioning workflow. The administrator creates a sensor device record, receives a one-time plaintext device token, assigns the sensor to a user, and attaches it to a plant owned by that user. If an unassigned sensor is attached to a plant, the backend can assign it to the plant owner automatically; however, an already assigned sensor cannot be attached to a plant owned by a different user. Regular users cannot create sensors, attach or detach sensors, or rotate device tokens. They can only view their assigned sensors, online or offline status, attached plant, last seen time, source label, and readings.

## 3. Plant Type and Knowledge Base

### What Is Outdated

Generic plant examples, old Monstera/Ficus examples, or text implying that multiple plant profiles are fully implemented should be revised.

### Why It Is Outdated

The current implemented plant knowledge base supports Golden pothos / Epipremnum aureum. Condition thresholds and recommendations are based on this profile.

### Replacement Paragraph

The current prototype focuses on Golden pothos, also known as Epipremnum aureum. The plant knowledge base stores threshold ranges and care guidance for this plant profile. The monitoring service evaluates current moisture, temperature, humidity, and light readings against this local knowledge base and produces condition status, health score, risk factors, explanations, and care recommendations.

## 4. Alerts, Notifications, and Recommendations

### What Is Outdated

Text that describes notifications only as future work is outdated. Text that treats alerts and notifications as the same concept should be separated.

### Why It Is Outdated

Alerts already existed as plant-condition events. Phase 4A added persisted in-app notifications created from newly created alerts. The frontend now has a notification bell/panel and unread state.

### Replacement Paragraph

The system separates alerts, recommendations, and notifications. Alerts represent detected plant condition issues and have a lifecycle managed by a finite-state workflow. Recommendations provide care guidance based on the current condition and the Golden pothos knowledge base. Persisted in-app notifications are created when new alerts are generated. Notifications are stored in the database, scoped to the current user, deduplicated by `dedupe_key`, and can be marked as read individually or in bulk. The backend exposes `/api/v1/notifications` endpoints and a `/api/v1/stream/notifications` SSE stream for real-time UI updates.

## 5. Internationalization

### What Is Outdated

Any text implying English-first UI only, or omitting localization, should be updated.

### Why It Is Outdated

The frontend is Kazakh-first by default and also supports Russian and English.

### Replacement Paragraph

The user interface is Kazakh-first by default, with Russian and English available through the language switcher. Main user-facing areas, including dashboard, plant details, alerts, notifications, settings, sensor views, and admin provisioning controls, are localized in all three languages.

## 6. Database and Migrations

### What Is Outdated

Database table lists that do not include notifications are outdated. Migration summaries that stop before Phase 4A are outdated.

### Why It Is Outdated

The backend migrations now include `0003_notifications`, which adds persisted notifications.

### Replacement Paragraph

The database schema includes users, plants, sensors, sensor readings, alerts, alert transitions, recommendations, system logs, and notifications. The latest migration set includes the initial MVP schema, IoT condition fields, and the notifications migration (`0003_notifications`). The notifications table stores user scope, notification type, severity, localization keys, JSON parameters, optional fallback title/message, related plant/alert/sensor references, deduplication key, read timestamp, and creation timestamp.

## 7. API Endpoint Appendix Updates

### Sensor Endpoints

Mark these endpoints as administrator-only:

- `POST /api/v1/sensors`
- `POST /api/v1/sensors/{sensor_id}/attach`
- `POST /api/v1/sensors/{sensor_id}/detach`
- `POST /api/v1/sensors/{sensor_id}/rotate-token`

Add this endpoint:

- `POST /api/v1/sensors/{sensor_id}/assign`

Keep this endpoint as read access:

- `GET /api/v1/sensors` - admin sees all sensors; regular users see only sensors assigned to them or attached to their own plants.

### Notification Endpoints

Add:

- `GET /api/v1/notifications?unread_only=false&limit=20&offset=0`
- `POST /api/v1/notifications/{notification_id}/read`
- `POST /api/v1/notifications/read-all`
- `GET /api/v1/stream/notifications`

Keep existing:

- `GET /api/v1/stream/alerts`
- `GET /api/v1/stream/dashboard/{plant_id}`

## 8. Figures and Tables to Update

Update the architecture diagram to show:

```text
Arduino Uno -> USB Serial -> Python Serial Gateway -> FastAPI -> PostgreSQL -> React frontend
```

Update the sensor lifecycle diagram to show:

```text
Admin creates sensor -> Admin copies one-time token -> Admin assigns user -> Admin attaches plant -> Gateway sends readings -> User views read-only sensor state
```

Update the database schema table to add:

- `notifications`

Update API endpoint tables to include:

- admin-only sensor mutation endpoints;
- `POST /api/v1/sensors/{sensor_id}/assign`;
- notification endpoints;
- `/api/v1/stream/notifications`.

Update testing tables to state:

- Backend tests: 37 passed.
- Migrations include `0003_notifications`.

## 9. Future Work That Can Stay Future Work

The following items are still future work and can remain in the thesis future-work section:

- email notifications;
- browser/web push notifications;
- subscription or rental payment reminders;
- background scheduler for sensor stale/offline notification generation;
- support for more plant species beyond Golden pothos / Epipremnum aureum;
- production deployment and long-term monitoring hardening.
