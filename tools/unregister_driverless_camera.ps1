$ErrorActionPreference = "Stop"
. "$PSScriptRoot\driverless_camera_common.ps1"

Invoke-DriverlessCamera -Action unregister
