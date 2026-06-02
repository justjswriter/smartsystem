$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PowerShellPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$GatewayScriptPath = Join-Path $ScriptDir "start_gateway.ps1"
$TaskName = "Smart Plant IoT Gateway"

if (-not (Test-Path $GatewayScriptPath)) {
    throw "start_gateway.ps1 was not found."
}

$Action = New-ScheduledTaskAction `
    -Execute $PowerShellPath `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$GatewayScriptPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel LeastPrivilege

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Starts Smart Plant Arduino serial gateway silently on Windows login." -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName

Write-Host "Installed and started hidden Windows startup task: $TaskName"
Write-Host "The gateway now runs in the background and waits for Arduino USB automatically."
Write-Host "Logs: $ScriptDir\logs\gateway.log"
