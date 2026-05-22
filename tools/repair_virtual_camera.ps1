$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$installScript = Join-Path $PSScriptRoot "install_virtual_camera.ps1"
$signScript = Join-Path $PSScriptRoot "sign_virtual_camera_test.ps1"
. "$PSScriptRoot\native_camera_common.ps1"

if (-not (Test-Path $installScript)) {
    throw "PhoneCam install script not found: $installScript"
}

Write-Host "Repairing PhoneCam virtual camera registration."
Write-Host "For public releases this action must use the Microsoft-signed package."

$catalog = Join-Path (Get-NativeCameraPackagePath) "phonecamcameradriver.cat"
if ((Test-Path $signScript) -and (Test-Path $catalog) -and -not (Test-MicrosoftSignedCatalog $catalog)) {
    & $signScript
}

& $installScript
& (Join-Path $PSScriptRoot "check_virtual_camera.ps1")
