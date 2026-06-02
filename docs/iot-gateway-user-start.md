# Smart Plant IoT Gateway User Start

This is the simple user-facing way to start Arduino data transfer after the web app is deployed.

## What The User Does

1. Connect Arduino Uno to the notebook with USB.
2. Double-click for manual visible start:

```text
iot/serial_gateway/start_gateway.bat
```

3. Leave the opened window running.

The gateway automatically looks for the Arduino COM port, reads JSON sensor data, and sends it to the deployed backend.

## Configuration

The configuration file is:

```text
iot/serial_gateway/gateway.env
```

Current values:

```env
BACKEND_URL=https://smartsystem-backens-smart-plant-system-mainly.fin1.bult.app
DEVICE_ID=arduino-uno-001
PORT=auto
BAUD_RATE=9600
SOIL_WET_RAW=260
SOIL_DRY_RAW=473
```

The `DEVICE_TOKEN` must match the token generated in the admin panel for the same sensor.

## Recommended Hidden Windows Autostart

To start the gateway automatically and silently when the user logs into Windows, run PowerShell in the gateway folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_autostart_task.ps1
```

After that, Windows Task Scheduler starts the gateway hidden in the background. The user does not need to keep a console window open.

The hidden gateway waits for Arduino USB automatically because `PORT=auto`.

Logs are written to:

```text
iot/serial_gateway/logs/gateway.log
```

To remove hidden autostart:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall_autostart_task.ps1
```

## When Bult Redeploy Is Needed

Bult redeploy is not needed for normal IoT operation. The gateway runs on the notebook and sends data to the already deployed backend.

Bult redeploy is needed only when backend/frontend code or Bult environment variables change.
