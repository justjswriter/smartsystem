$ErrorActionPreference = "Stop"

$TaskName = "Smart Plant IoT Gateway"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed Windows startup task: $TaskName"
} else {
    Write-Host "Task was not installed: $TaskName"
}
