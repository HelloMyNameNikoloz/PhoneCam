$ErrorActionPreference = "Stop"

function Find-MSBuild {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
    )

    $msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $msbuild) {
        throw "MSBuild Build Tools were not found. Install Visual Studio Build Tools 2022."
    }
    return $msbuild
}

function Get-WindowsKitRoot {
    $root = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10"
    if (-not (Test-Path $root)) {
        throw "Windows Kits root was not found at '$root'. Install Windows SDK and WDK."
    }
    return (Resolve-Path $root).Path.TrimEnd("\")
}

function Get-PreferredKitVersion($kitRoot) {
    $preferred = "10.0.26100.0"
    $versions = Get-ChildItem (Join-Path $kitRoot "build") -Directory |
        Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } |
        Sort-Object Name -Descending

    foreach ($version in @($preferred) + @($versions.Name)) {
        if (-not $version) { continue }
        $wdkProps = Join-Path $kitRoot "build\$version\WindowsDriver.Common.targets"
        $uapProps = Join-Path $kitRoot "DesignTime\CommonConfiguration\Neutral\UAP\$version\UAP.props"
        $sdkHeader = Join-Path $kitRoot "Include\$version\shared\sdkddkver.h"
        if ((Test-Path $wdkProps) -and (Test-Path $uapProps) -and (Test-Path $sdkHeader)) {
            return $version
        }
    }

    throw "No complete Windows SDK/WDK version was found. Install Windows SDK and WDK 10.0.26100."
}

function Get-WdfVersion($kitRoot, $platform) {
    $versions = Get-ChildItem (Join-Path $kitRoot "Include\wdf\umdf") -Directory |
        Sort-Object Name -Descending

    foreach ($version in $versions.Name) {
        $header = Join-Path $kitRoot "Include\wdf\umdf\$version\wdf.h"
        $library = Join-Path $kitRoot "Lib\wdf\umdf\$platform\$version\WdfDriverStubUm.lib"
        if ((Test-Path $header) -and (Test-Path $library)) {
            return $version
        }
    }

    throw "WDF UMDF headers/libs are missing. Expected wdf.h under '$kitRoot\Include\wdf\umdf' and WdfDriverStubUm.lib under '$kitRoot\Lib\wdf\umdf\$platform'."
}

$root = Split-Path -Parent $PSScriptRoot
$solution = Join-Path $root "native\phonecam_virtual_camera\PhoneCamVirtualCamera.sln"
$platform = "x64"
$msbuild = Find-MSBuild
$kitRoot = Get-WindowsKitRoot
$kitVersion = Get-PreferredKitVersion $kitRoot
$wdfVersion = Get-WdfVersion $kitRoot $platform

$kitRootForMsBuild = ($kitRoot -replace "\\", "/") + "/"
$arguments = @(
    $solution,
    "/p:Configuration=Release",
    "/p:Platform=$platform",
    "/p:PlatformTarget=$platform",
    "/p:PlatformToolset=v143",
    "/p:WindowsTargetPlatformVersion=$kitVersion",
    "/p:PhoneCamUseInstalledWdkProps=true",
    "/p:WDKContentRoot=$kitRootForMsBuild",
    "/p:WDKBuildFolder=$kitVersion",
    "/p:PhoneCamWdfVersion=$wdfVersion",
    "/p:SkipPackageVerification=true",
    "/m"
)

Write-Host "Using Windows Kits root: $kitRoot"
Write-Host "Using SDK/WDK version: $kitVersion"
Write-Host "Using UMDF WDF version: $wdfVersion"

& $msbuild @arguments
