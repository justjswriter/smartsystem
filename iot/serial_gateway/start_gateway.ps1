$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "gateway.env"
$PythonPath = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$GatewayPath = Join-Path $ScriptDir "serial_gateway.py"

if (-not (Test-Path $ConfigPath)) {
    Copy-Item (Join-Path $ScriptDir "gateway.env.example") $ConfigPath
    Write-Host "Created gateway.env. Fill DEVICE_TOKEN, then run this file again."
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-Path $PythonPath)) {
    Write-Host "Python virtual environment was not found. Run setup first or create .venv in this folder."
    Read-Host "Press Enter to close"
    exit 1
}

Get-Content $ConfigPath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }
    $parts = $line.Split("=", 2)
    if ($parts.Count -eq 2) {
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

$port = if ($env:PORT) { $env:PORT } else { "auto" }
$sourceLabel = if ($env:SOURCE_LABEL -and $env:SOURCE_LABEL -ne "auto") { $env:SOURCE_LABEL } else { "" }

$baseArgs = @(
    $GatewayPath,
    "--port", $port,
    "--baud-rate", $(if ($env:BAUD_RATE) { $env:BAUD_RATE } else { "9600" }),
    "--backend-url", $env:BACKEND_URL,
    "--device-id", $env:DEVICE_ID,
    "--device-token", $env:DEVICE_TOKEN,
    "--soil-wet-raw", $(if ($env:SOIL_WET_RAW) { $env:SOIL_WET_RAW } else { "260" }),
    "--soil-dry-raw", $(if ($env:SOIL_DRY_RAW) { $env:SOIL_DRY_RAW } else { "473" }),
    "--log-level", $(if ($env:LOG_LEVEL) { $env:LOG_LEVEL } else { "INFO" })
)

if ($sourceLabel) {
    $baseArgs += @("--source-label", $sourceLabel)
}

Write-Host "Smart Plant IoT Gateway"
Write-Host "Backend: $env:BACKEND_URL"
Write-Host "Device:  $env:DEVICE_ID"
Write-Host "Port:    $port"
Write-Host ""
Write-Host "Leave this window open while Arduino is connected."
Write-Host "Press Ctrl+C to stop."
Write-Host ""

while ($true) {
    & $PythonPath @baseArgs
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 130) {
        exit 0
    }
    Write-Host ""
    Write-Host "Gateway stopped with exit code $exitCode. Retrying in 10 seconds..."
    Start-Sleep -Seconds 10
}
