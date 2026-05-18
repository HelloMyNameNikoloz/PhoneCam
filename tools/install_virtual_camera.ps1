$ErrorActionPreference = "Stop"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell session."
}

$root = Split-Path -Parent $PSScriptRoot
$package = Join-Path $root "native\phonecam_virtual_camera\x64\Release\PhoneCamCameraDriver"
$inf = Join-Path $package "PhoneCamCameraDriver.inf"

if (-not (Test-Path $inf)) {
    throw "Driver package not found. Run tools\build_native_camera.ps1 first."
}

$devgen = Get-Command devgen.exe -ErrorAction SilentlyContinue
if (-not $devgen) {
    throw "devgen.exe was not found. Install the Windows Driver Kit tools."
}

& $devgen.Source /add /bus ROOT /hardwareid root\PhoneCamVirtualCamera
& pnputil /add-driver $inf /install
