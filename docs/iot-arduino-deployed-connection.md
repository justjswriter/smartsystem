# IoT Arduino Connection Guide

This guide explains how to connect the Arduino Uno sensor node to the deployed Smart Plant web application.

## Current Deployment

Frontend:

```text
https://smartsystem-frontend-smart-plant-system-new.fin1.bult.app
```

Backend:

```text
https://smartsystem-backens-smart-plant-system-mainly.fin1.bult.app
```

Backend health check:

```text
https://smartsystem-backens-smart-plant-system-mainly.fin1.bult.app/health
```

## Project Files

Arduino firmware:

```text
iot/arduino_uno_sensor_node/arduino_uno_sensor_node.ino
```

Python serial gateway:

```text
iot/serial_gateway/serial_gateway.py
```

Gateway dependencies:

```text
iot/serial_gateway/requirements.txt
```

## Data Flow

```text
Arduino Uno -> USB Serial COM port -> Python serial_gateway.py -> deployed backend -> PostgreSQL -> frontend dashboard
```

The Arduino Uno does not send data to the internet directly. It prints sensor data through USB Serial. The Python gateway reads those serial lines and forwards them to the deployed backend API.

## 1. Upload Arduino Firmware

1. Open Arduino IDE.
2. Open:

```text
iot/arduino_uno_sensor_node/arduino_uno_sensor_node.ino
```

3. Select:

```text
Board: Arduino Uno
Port: COM3
Baud rate: 9600
```

4. Upload the sketch.

## 2. Check Arduino Serial Output

Open Arduino IDE Serial Monitor and set baud rate to:

```text
9600
```

Expected output:

```json
{"soil_raw":40,"humidity":36.5,"temperature":27.1,"light_raw":120}
```

If data appears, close Serial Monitor before running the Python gateway. Only one program can use the COM port at the same time.

## 3. Create Sensor In The Web App

Open the frontend:

```text
https://smartsystem-frontend-smart-plant-system-new.fin1.bult.app
```

Log in as admin.

Create a sensor:

```text
device_id: demo-sensor-001
type: multi
```

Copy the generated device token. It is shown only once.

## 4. Attach Sensor To User And Plant

In the admin panel:

1. Assign the sensor to the user.
2. Attach the sensor to the user's plant.

The backend needs the sensor to be attached to a plant before readings can appear on the dashboard.

## 5. Open Gateway Folder

In PowerShell:

```powershell
cd "C:\Users\Admin\Downloads\smartsystem-new-report-updates\smartsystem-new-report-updates\iot\serial_gateway"
```

## 6. Run The Gateway

Replace `TOKEN_FROM_ADMIN` with the token copied from the admin panel:

```powershell
.\.venv\Scripts\python.exe serial_gateway.py --port COM3 --baud-rate 9600 --backend-url https://smartsystem-backens-smart-plant-system-mainly.fin1.bult.app --device-id demo-sensor-001 --device-token "TOKEN_FROM_ADMIN" --source-label serial:COM3 --soil-dry-raw 1023 --log-level DEBUG
```

If Arduino uses another port, replace `COM3`, for example:

```powershell
--port COM4
```

## 7. Successful Result

The gateway should print:

```text
Accepted by backend
```

In the web application:

- Sensor status becomes online.
- `last_seen_at` updates.
- Plant dashboard receives moisture, temperature, humidity, and light values.
- Alerts and recommendations appear when readings are critical.

## Troubleshooting

### Could not open serial port

Close Arduino IDE Serial Monitor and check that the correct COM port is selected.

### 401

The device token is incorrect. Rotate or recreate the sensor token in the admin panel.

### Sensor device_id was not found

The `device_id` in the gateway command does not match the `device_id` created in the admin panel.

### Sensor is not attached to a plant

Attach the sensor to a plant in the admin panel.

### Skipping non-JSON serial line

Arduino is printing text that is not valid JSON. Check Serial Monitor output and make sure the uploaded firmware is correct.

## Notes

This setup requires the notebook or PC to stay connected to Arduino through USB while the gateway is running. Wi-Fi is not required for Arduino Uno.
