$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$solution = Join-Path $root "native\phonecam_virtual_camera\PhoneCamVirtualCamera.sln"
$candidates = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)
$msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $msbuild) {
    throw "MSBuild Build Tools were not found."
}

$required = @("WindowsApplicationForDrivers10.0", "WindowsUserModeDriver10.0")
$vsRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $msbuild))
$toolsetRoot = Join-Path $vsRoot "Microsoft\VC\v170\Platforms\x64\PlatformToolsets"
if (-not (Test-Path $toolsetRoot)) {
    $toolsetRoot = Join-Path $vsRoot "Microsoft\VC\v160\Platforms\x64\PlatformToolsets"
}
$missing = $required | Where-Object { -not (Test-Path (Join-Path $toolsetRoot $_)) }
if ($missing.Count -gt 0) {
    throw "Missing WDK Visual Studio toolsets: $($missing -join ', '). Install the Windows Driver Kit with VS integration."
}

& $msbuild $solution /p:Configuration=Release /p:Platform=x64 /m
