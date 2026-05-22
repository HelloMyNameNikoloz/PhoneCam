$ErrorActionPreference = "Stop"
. "$PSScriptRoot\driverless_camera_common.ps1"

Write-Host "Repairing the PhoneCam Windows 11 driverless virtual camera."
Invoke-DriverlessCamera -Action repair
Write-Host "PhoneCam camera repair completed."
