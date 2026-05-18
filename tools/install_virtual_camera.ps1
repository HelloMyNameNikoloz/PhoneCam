$ErrorActionPreference = "Stop"
. "$PSScriptRoot\native_camera_common.ps1"

$package = Get-NativeCameraPackagePath
$inf = Join-Path $package "PhoneCamCameraDriver.inf"
$catalog = Join-Path $package "phonecamcameradriver.cat"

if (-not (Test-Path $inf)) {
    throw "Driver package not found. Run tools\build_native_camera.ps1 first."
}
if (-not (Test-Path $catalog)) {
    throw "Driver catalog not found. Run tools\build_native_camera.ps1 first."
}

Assert-CatalogSigned -CatalogPath $catalog
Assert-Elevated "install the PhoneCam virtual camera"
Assert-TestSigningEnabled

$devgenPath = Find-WdkTool -Name "devgen.exe"

& $devgenPath /add /bus ROOT /hardwareid root\PhoneCamVirtualCamera
& pnputil /add-driver $inf /install
