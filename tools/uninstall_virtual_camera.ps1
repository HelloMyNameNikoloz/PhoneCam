$ErrorActionPreference = "Stop"
. "$PSScriptRoot\driverless_camera_common.ps1"

Write-Host "Unregistering the PhoneCam Windows 11 driverless virtual camera."
try {
    Invoke-DriverlessCamera -Action unregister
}
catch {
    Write-Warning $_.Exception.Message
}

$dataDir = Join-Path $env:ProgramData "PhoneCam"
if (Test-Path $dataDir) {
    foreach ($file in @("framebuffer.bin", "native_stats.bin", "native_settings.txt", "native_camera.log")) {
        Remove-Item (Join-Path $dataDir $file) -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "PhoneCam camera cleanup completed."
