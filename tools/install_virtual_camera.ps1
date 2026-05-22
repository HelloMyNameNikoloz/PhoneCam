param(
    [switch]$KeepDevice
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\native_camera_common.ps1"

function Get-PhoneCamDriverPackages {
    $packages = @()
    $current = @{}
    foreach ($line in (& pnputil /enum-drivers /class Camera)) {
        if ($line -match "^\s*$") {
            if (Test-PhoneCamPackage $current) { $packages += $current }
            $current = @{}
            continue
        }
        if ($line -match "^\s*Published Name:\s*(.+)$") { $current.PublishedName = $Matches[1].Trim() }
        if ($line -match "^\s*Original Name:\s*(.+)$") { $current.OriginalName = $Matches[1].Trim() }
        if ($line -match "^\s*Provider Name:\s*(.+)$") { $current.ProviderName = $Matches[1].Trim() }
    }
    if (Test-PhoneCamPackage $current) { $packages += $current }
    return $packages
}

function Test-PhoneCamPackage($package) {
    return $package.PublishedName -and
        $package.OriginalName -eq "phonecamcameradriver.inf" -and
        $package.ProviderName -eq "PhoneCam"
}

function Remove-PhoneCamDevices {
    Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
        Where-Object { $_.FriendlyName -eq "PhoneCam" -and $_.InstanceId -like "ROOT\DEVGEN\*" } |
        ForEach-Object {
            Write-Host "Removing PhoneCam device: $($_.InstanceId)"
            & pnputil /remove-device $_.InstanceId
        }
}

function Remove-PhoneCamDriverPackages {
    foreach ($driver in Get-PhoneCamDriverPackages) {
        Write-Host "Deleting old PhoneCam driver package: $($driver.PublishedName)"
        & pnputil /delete-driver $driver.PublishedName /uninstall /force
    }
}

function Stop-CameraFrameServer {
    foreach ($serviceName in @("FrameServer", "FrameServerMonitor")) {
        $service = Get-Service $serviceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Host "Stopping $serviceName"
            Stop-Service $serviceName -Force -ErrorAction SilentlyContinue
        }
    }
}

function Start-CameraFrameServer {
    foreach ($serviceName in @("FrameServer", "FrameServerMonitor")) {
        $service = Get-Service $serviceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -ne "Running") {
            Start-Service $serviceName -ErrorAction SilentlyContinue
        }
    }
}

function Initialize-PhoneCamDataDirectory {
    $dataDir = Join-Path $env:ProgramData "PhoneCam"
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    & icacls $dataDir /grant "*S-1-5-32-545:(OI)(CI)M" "*S-1-5-19:(OI)(CI)RX" "*S-1-5-20:(OI)(CI)RX" | Out-Null
    return $dataDir
}

$package = Get-NativeCameraPackagePath
$inf = Join-Path $package "PhoneCamCameraDriver.inf"
$catalog = Join-Path $package "phonecamcameradriver.cat"

if (-not (Test-Path $inf)) { throw "Driver package not found. Run tools\build_native_camera.ps1 first." }
if (-not (Test-Path $catalog)) { throw "Driver catalog not found. Run tools\build_native_camera.ps1 first." }

Assert-CatalogSigned -CatalogPath $catalog
Assert-Elevated "install the PhoneCam virtual camera"
if (-not (Test-MicrosoftSignedCatalog -CatalogPath $catalog)) {
    Assert-TestSigningEnabled
}

$consumers = @(Get-Process PhoneCam, obs64, obs32, obs, WindowsCamera, Video.UI -ErrorAction SilentlyContinue)
if ($consumers.Count -gt 0) {
    $names = ($consumers | ForEach-Object { "$($_.ProcessName) (PID $($_.Id))" }) -join ", "
    throw "Close camera apps before installing PhoneCam updates. Running processes: $names"
}

$dataDir = Initialize-PhoneCamDataDirectory
$nativeLog = Join-Path $dataDir "native_camera.log"
Remove-Item $nativeLog -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $dataDir "native_stats.bin") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $dataDir "framebuffer.bin") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $dataDir "native_settings.txt") -Force -ErrorAction SilentlyContinue

Stop-CameraFrameServer
if (-not $KeepDevice) {
    Remove-PhoneCamDevices
}
Remove-PhoneCamDriverPackages

$devgenPath = Find-WdkTool -Name "devgen.exe"
if (-not $KeepDevice) {
    & $devgenPath /add /bus ROOT /hardwareid root\PhoneCamVirtualCamera
}

& pnputil /add-driver $inf /install
Start-CameraFrameServer

Write-Host "Installed PhoneCam driver packages:"
Get-PhoneCamDriverPackages | Format-Table -AutoSize
