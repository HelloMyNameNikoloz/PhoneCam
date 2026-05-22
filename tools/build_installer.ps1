param(
    [string]$Configuration = "Release",
    [string]$Version = "0.1.0",
    [string]$WixVersion = "6.0.2"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Get-Wix {
    $localWix = Join-Path $root ".tools\wix\wix.exe"
    if (Test-Path $localWix) { return $localWix }

    $pathWix = Get-Command wix -ErrorAction SilentlyContinue
    if ($pathWix) { return $pathWix.Source }

    $dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if (-not $dotnet) {
        throw "WiX Toolset was not found. Install .NET SDK, then run this script again."
    }

    $toolDir = Split-Path -Parent $localWix
    New-Item -ItemType Directory -Path $toolDir -Force | Out-Null
    & $($dotnet.Source) tool install wix --tool-path $toolDir --version $WixVersion | Out-Null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $localWix)) {
        throw "Failed to install WiX CLI into $toolDir."
    }
    return $localWix
}

function Assert-File($path, $message) {
    if (-not (Test-Path $path)) { throw "$message Missing: $path" }
}

function Get-MsiProductVersion([string]$value) {
    $clean = $value.TrimStart("v")
    if ($clean -match "^(\d+)\.(\d+)\.(\d+)") {
        return "$($Matches[1]).$($Matches[2]).$($Matches[3])"
    }
    throw "Version must start with semantic version format, for example v1.0.0-beta.1 or 1.0.0."
}

$appExe = Join-Path $root "phonecam\dist\PhoneCam.exe"
$apk = Join-Path $root "phonecam\assets\PhoneCamCompanion.apk"
$cameraDir = Join-Path $root "native\phonecam_virtual_camera\x64\Release\Driverless"
$outDir = Join-Path $root "release"
$iconFile = Join-Path $root "assets\icon.ico"
$scripts = @(
    "repair_virtual_camera.ps1",
    "uninstall_virtual_camera.ps1",
    "driverless_camera_common.ps1"
)

# Auto-generate icon.ico if missing
if (-not (Test-Path $iconFile)) {
    Write-Host "assets/icon.ico is missing. Attempting to generate it..."
    $generator = Join-Path $root "tools\assets\generate_icons.ps1"
    if (Test-Path $generator) {
        powershell -ExecutionPolicy Bypass -File $generator
    }
}

Assert-File $appExe "Build the desktop app first with: python phonecam\build_tools\build_exe.py."
Assert-File $apk "Build the Android companion first with: .\tools\build_android_companion.ps1."
Assert-File $iconFile "Build the assets/icon.ico first with: .\tools\assets\generate_icons.ps1."
Assert-File (Join-Path $cameraDir "PhoneCamCameraCtl.exe") "Build the driverless camera files first with: .\tools\build_driverless_camera.ps1."
Assert-File (Join-Path $cameraDir "PhoneCamVirtualCamera.dll") "Build the driverless camera files first with: .\tools\build_driverless_camera.ps1."

foreach ($script in $scripts) {
    Assert-File (Join-Path $PSScriptRoot $script) "Installer script input is missing."
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$output = Join-Path $outDir "PhoneCam-Setup-$Version.msi"
$wix = Get-Wix

$wixArgs = @(
    "build",
    (Join-Path $root "installer\wix\PhoneCam.wxs"),
    "-d", "SourceRoot=$root",
    "-d", "AppExe=$appExe",
    "-d", "CompanionApk=$apk",
    "-d", "IconFile=$iconFile",
    "-d", "ToolsDir=$PSScriptRoot",
    "-d", "CameraDir=$cameraDir",
    "-d", "ProductVersion=$(Get-MsiProductVersion $Version)",
    "-o", $output
)

& $wix @wixArgs
if ($LASTEXITCODE -ne 0) {
    throw "WiX build failed."
}

Write-Host "Built $output"
