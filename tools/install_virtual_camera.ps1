param(
    [switch]$Recreate
)

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

$obsProcesses = @(Get-Process obs64, obs32, obs -ErrorAction SilentlyContinue)
if ($obsProcesses.Count -gt 0) {
    $names = ($obsProcesses | ForEach-Object { "$($_.ProcessName) (PID $($_.Id))" }) -join ", "
    throw "Close OBS before installing PhoneCam virtual camera updates. Running OBS processes: $names"
}

$devgenPath = Find-WdkTool -Name "devgen.exe"
$existingDevices = @(Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FriendlyName -eq "PhoneCam" -and $_.InstanceId -like "ROOT\DEVGEN\*"
    })

if ($Recreate) {
    $existingDevices | ForEach-Object {
        Write-Host "Removing existing PhoneCam instance: $($_.InstanceId)"
        & pnputil /remove-device $_.InstanceId
    }
    $existingDevices = @()
}

if ($existingDevices.Count -eq 0) {
    & $devgenPath /add /bus ROOT /hardwareid root\PhoneCamVirtualCamera
} else {
    Write-Host "Updating existing PhoneCam instance:"
    $existingDevices | Select-Object Status, FriendlyName, InstanceId | Format-Table -AutoSize
}

& pnputil /add-driver $inf /install
