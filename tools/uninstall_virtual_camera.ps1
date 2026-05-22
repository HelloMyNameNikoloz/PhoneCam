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

Assert-Elevated "uninstall the PhoneCam virtual camera"

Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -eq "PhoneCam" -and $_.InstanceId -like "ROOT\DEVGEN\*" } |
    ForEach-Object {
        Write-Host "Removing PhoneCam device: $($_.InstanceId)"
        & pnputil /remove-device $_.InstanceId
    }

foreach ($driver in Get-PhoneCamDriverPackages) {
    Write-Host "Deleting PhoneCam driver package: $($driver.PublishedName)"
    & pnputil /delete-driver $driver.PublishedName /uninstall /force
}

$dataDir = Join-Path $env:ProgramData "PhoneCam"
if (Test-Path $dataDir) {
    Remove-Item (Join-Path $dataDir "framebuffer.bin") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $dataDir "native_stats.bin") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $dataDir "native_settings.txt") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $dataDir "native_camera.log") -Force -ErrorAction SilentlyContinue
}
