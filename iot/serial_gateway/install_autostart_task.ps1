$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ScriptDir "start_gateway.bat"
$TaskName = "Smart Plant IoT Gateway"

if (-not (Test-Path $BatPath)) {
    throw "start_gateway.bat was not found."
}

$Action = New-ScheduledTaskAction -Execute $BatPath
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Starts Smart Plant Arduino serial gateway on Windows login." -Force | Out-Null

Write-Host "Installed Windows startup task: $TaskName"
Write-Host "It will start after Windows login. You can also run start_gateway.bat manually."
