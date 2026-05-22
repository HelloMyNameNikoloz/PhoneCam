param(
    [switch]$SkipNative,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Write-Host "Building Android companion..."
& (Join-Path $PSScriptRoot "build_android_companion.ps1")

Write-Host "Building Windows desktop EXE..."
Push-Location (Join-Path $root "phonecam")
try {
    python .\build_tools\build_exe.py
}
finally {
    Pop-Location
}

if (-not $SkipNative) {
    Write-Host "Building native virtual camera package..."
    & (Join-Path $PSScriptRoot "build_native_camera.ps1")
}

if (-not $SkipInstaller) {
    Write-Host "Building WiX MSI..."
    & (Join-Path $PSScriptRoot "build_installer.ps1")
}
