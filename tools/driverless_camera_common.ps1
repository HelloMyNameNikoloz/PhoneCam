$ErrorActionPreference = "Stop"

function Get-PhoneCamRoot {
    $scriptRoot = Split-Path -Parent $PSScriptRoot
    $installedRoot = Split-Path -Parent $PSScriptRoot
    if (Test-Path (Join-Path $installedRoot "camera\PhoneCamCameraCtl.exe")) {
        return $installedRoot
    }
    return $scriptRoot
}

function Get-DriverlessCameraPackage {
    $root = Get-PhoneCamRoot
    $candidates = @(
        (Join-Path $root "camera"),
        (Join-Path $root "native\phonecam_virtual_camera\x64\Release\Driverless")
    )
    foreach ($candidate in $candidates) {
        $tool = Join-Path $candidate "PhoneCamCameraCtl.exe"
        $source = Join-Path $candidate "PhoneCamVirtualCamera.dll"
        if ((Test-Path $tool) -and (Test-Path $source)) {
            return [PSCustomObject]@{
                Tool = $tool
                Source = $source
            }
        }
    }
    throw "Driverless PhoneCam camera files are missing. Build with tools\build_driverless_camera.ps1 or repair the installation."
}

function Invoke-DriverlessCamera {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("status", "register", "repair", "unregister")]
        [string]$Action
    )
    $package = Get-DriverlessCameraPackage
    & $package.Tool $Action $package.Source
    if ($LASTEXITCODE -ne 0) {
        throw "PhoneCam camera $Action failed."
    }
}
