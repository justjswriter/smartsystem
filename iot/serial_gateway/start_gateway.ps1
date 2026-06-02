$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "gateway.env"
$PythonPath = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$GatewayPath = Join-Path $ScriptDir "serial_gateway.py"
$LogDir = Join-Path $ScriptDir "logs"
$LogPath = Join-Path $LogDir "gateway.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-GatewayLog {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Write-Host $line
    Add-Content -Path $LogPath -Value $line
}

if (-not (Test-Path $ConfigPath)) {
    Copy-Item (Join-Path $ScriptDir "gateway.env.example") $ConfigPath
    Write-GatewayLog "Created gateway.env. Fill DEVICE_TOKEN, then run this file again."
    Read-Host "Press Enter to close"
    exit 1
}

if (-not (Test-Path $PythonPath)) {
    Write-GatewayLog "Python virtual environment was not found. Run setup first or create .venv in this folder."
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

Write-GatewayLog "Smart Plant IoT Gateway starting"
Write-GatewayLog "Backend: $env:BACKEND_URL"
Write-GatewayLog "Device:  $env:DEVICE_ID"
Write-GatewayLog "Port:    $port"

while ($true) {
    & $PythonPath @baseArgs 2>&1 | Tee-Object -FilePath $LogPath -Append
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 130) {
        exit 0
    }
    Write-GatewayLog "Gateway stopped with exit code $exitCode. Retrying in 10 seconds..."
    Start-Sleep -Seconds 10
}
