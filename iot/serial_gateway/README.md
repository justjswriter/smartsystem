# Arduino Uno USB Serial Gateway

This gateway connects the real Arduino Uno sensor node to the existing FastAPI ingestion endpoint.

Data flow:

```text
Arduino Uno -> USB Serial COM port -> Python Serial Gateway -> FastAPI backend -> PostgreSQL -> frontend dashboard
```

The Arduino Uno does not use Wi-Fi and does not know the backend URL, device id, device token, or plant id. It only prints one JSON line every 5 seconds over USB Serial.

## 1. Upload Arduino firmware

1. Open Arduino IDE.
2. Open `iot/arduino_uno_sensor_node/arduino_uno_sensor_node.ino`.
3. Select `Board: Arduino Uno`.
4. Select the actual Arduino port, for example `COM3`.
5. Upload the sketch.
6. Optional check: open Serial Monitor at `9600` baud.

Expected Serial Monitor output:

```json
{"soil_raw":438,"humidity":36.5,"temperature":27.1,"light_raw":120}
{"soil_raw":1023,"humidity":null,"temperature":null,"light_raw":5}
```

If Serial Monitor is open, close it before running the Python gateway. Only one process can use the COM port at a time.

## 2. Start backend, database, and frontend

Backend and PostgreSQL:

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\practice-backend
docker compose up -d
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\smart-plant-frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Useful backend checks:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## 3. Provision and attach a backend sensor

1. Open `http://127.0.0.1:5173`.
2. Log in as a regular user and create or choose a plant.
3. Log in as admin and open the Admin page.
4. Create a new sensor:
   - Device ID: `arduino-uno-001`
   - Type: `multi`
5. Copy the shown device token. It is shown once.
6. Assign the sensor to the user who owns the plant.
7. Attach the sensor to that plant.
8. Return to the regular user account if you want to verify the read-only Sensors page.

The gateway must use the same `device_id` and device token.

## 4. Install gateway dependencies

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\iot\serial_gateway
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## 5. Run the gateway

Replace `COM3` with the Arduino port and replace `<TOKEN>` with the device token from the frontend.

```powershell
cd C:\Users\darig\CursorProjects\smartsystem\iot\serial_gateway
.\.venv\Scripts\python serial_gateway.py `
  --port COM3 `
  --baud-rate 9600 `
  --backend-url http://127.0.0.1:8000 `
  --device-id arduino-uno-001 `
  --device-token <TOKEN> `
  --source-label serial:COM3 `
  --interval 5 `
  --http-timeout 10 `
  --retry-delay 5
```

Successful log example:

```text
Accepted by backend: sensor_data_id=123 payload={'moisture': 72.3, 'temperature': 27.1, 'humidity': 36.5, 'light': 117.3}
```

## 6. Verify end-to-end delivery

1. Gateway logs show `Accepted by backend`.
2. Frontend Sensors page shows the sensor as `online` and updates `last_seen_at`.
3. Frontend Sensors page shows `last_ingest_source` as `serial:COM3`.
4. Plant dashboard shows latest moisture, temperature, humidity, and light score values.
5. Critical readings generate alerts and recommendations through the existing backend logic.

Backend endpoint used by the gateway:

```http
POST http://127.0.0.1:8000/api/v1/ingest/sensors/{device_id}/data
X-Device-Token: <TOKEN>
X-Ingest-Source: serial:COM3
Content-Type: application/json
```

Payload sent by gateway:

```json
{
  "moisture": 72.3,
  "temperature": 27.1,
  "humidity": 36.5,
  "light": 117.3
}
```

## Calibration

The Arduino sends raw values and the gateway normalizes them before sending to the backend.

- Soil moisture: `438 = wet = 100%`, `1023 = dry = 0%`
- Light: `light = light_raw / 1023 * 1000`
- Temperature passes through as a number or `null`
- Humidity is clamped to `0..100` and gets a default `+20` percentage point calibration offset because inexpensive DHT modules often under-read in dry indoor rooms. Use `--humidity-offset 0` if the sensor is calibrated.

The light value is a normalized score for the project dashboard, not real lux.

## Troubleshooting

- `Could not open serial port`: close Arduino IDE Serial Monitor and check the COM port.
- `401`: the device token does not match the backend sensor.
- `Sensor device_id was not found`: ask/admin-provision the sensor with the same `device_id`.
- `Sensor is not attached to a plant`: attach the sensor in the admin provisioning UI.
- `Backend is unavailable`: check that FastAPI is running on `http://127.0.0.1:8000`.
- `Skipping non-JSON serial line`: the gateway ignored a debug/startup line and will continue reading.
