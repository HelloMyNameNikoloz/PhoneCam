param(
    [string]$Version = "0.1.0-dev",
    [string]$AndroidOutputDir = "",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Write-Host "Building Android companion..."
$androidArgs = @{ Version = $Version }
if ($AndroidOutputDir) { $androidArgs.OutputDir = $AndroidOutputDir }
& (Join-Path $PSScriptRoot "build_android_companion.ps1") @androidArgs

Write-Host "Building Windows desktop EXE..."
$versionFile = Join-Path $root "phonecam\assets\version.txt"
$previousVersion = if (Test-Path $versionFile) { Get-Content $versionFile -Raw } else { "" }
Set-Content -Path $versionFile -Value $Version.TrimStart("v") -Encoding utf8
Push-Location (Join-Path $root "phonecam")
try {
    python .\build_tools\build_exe.py
}
finally {
    Pop-Location
    Set-Content -Path $versionFile -Value $previousVersion.Trim() -Encoding utf8
}

Write-Host "Building driverless Windows 11 camera files..."
& (Join-Path $PSScriptRoot "build_driverless_camera.ps1")

if (-not $SkipInstaller) {
    Write-Host "Building WiX MSI..."
    & (Join-Path $PSScriptRoot "build_installer.ps1") -Version $Version
}
