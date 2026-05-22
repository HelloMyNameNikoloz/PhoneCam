param(
    [string]$Configuration = "Release",
    [string]$Version = "0.1.0",
    [string]$WixVersion = "6.0.2",
    [switch]$RequireSignedDriver,
    [switch]$SkipDriver
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

function Get-Wix {
    $localWix = Join-Path $root ".tools\wix\wix.exe"
    if (Test-Path $localWix) { return $localWix }

    $dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
    if (-not $dotnet) {
        throw "WiX Toolset was not found and dotnet is unavailable. Install .NET SDK or put wix.exe on PATH."
    }

    $toolDir = Split-Path -Parent $localWix
    New-Item -ItemType Directory -Path $toolDir -Force | Out-Null
    & $($dotnet.Source) tool install wix --tool-path $toolDir --version $WixVersion
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $localWix)) {
        throw "Failed to install WiX CLI into $toolDir."
    }
    return $localWix
}

function Assert-File($path, $message) {
    if (-not (Test-Path $path)) { throw "$message Missing: $path" }
}

$appExe = Join-Path $root "phonecam\dist\PhoneCam.exe"
$apk = Join-Path $root "phonecam\assets\PhoneCamCompanion.apk"
$driver = Join-Path $root "native\phonecam_virtual_camera\x64\Release\PhoneCamCameraDriver"
$outDir = Join-Path $root "release"
$scripts = @(
    "repair_virtual_camera.ps1",
    "install_virtual_camera.ps1",
    "uninstall_virtual_camera.ps1",
    "check_virtual_camera.ps1",
    "native_camera_common.ps1"
)

Assert-File $appExe "Build the desktop app first with: python phonecam\build_tools\build_exe.py."
Assert-File $apk "Build the Android companion first with: .\tools\build_android_companion.ps1."
foreach ($script in $scripts) {
    Assert-File (Join-Path $PSScriptRoot $script) "Installer script input is missing."
}

if (-not $SkipDriver) {
    foreach ($file in @(
        "PhoneCamCameraDriver.inf",
        "phonecamcameradriver.cat",
        "PhoneCamCameraDriver.dll",
        "PhoneCamVirtualCamera.dll"
    )) {
        Assert-File (Join-Path $driver $file) "Build and sign the native camera package first. Expected driver file is missing."
    }
    $catalog = Join-Path $driver "phonecamcameradriver.cat"
    $signature = Get-AuthenticodeSignature $catalog
    if ($signature.Status -ne "Valid") {
        $message = "Driver catalog is not signed or not trusted: $catalog. Run tools\sign_virtual_camera_test.ps1 from elevated PowerShell for local dev, or use a Microsoft-signed package for public release."
        if ($RequireSignedDriver) { throw $message }
        Write-Warning $message
    }
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$output = Join-Path $outDir "PhoneCam-$Version-$Configuration.msi"
$wix = Get-Wix

$wixArgs = @(
    "build",
    (Join-Path $root "installer\wix\PhoneCam.wxs"),
    "-d", "SourceRoot=$root",
    "-d", "AppExe=$appExe",
    "-d", "CompanionApk=$apk",
    "-d", "ToolsDir=$PSScriptRoot",
    "-d", "DriverDir=$driver",
    "-d", "ProductVersion=$Version",
    "-d", "IncludeDriver=$([int](-not $SkipDriver))",
    "-o", $output
)

& $wix @wixArgs

if ($LASTEXITCODE -ne 0) {
    throw "WiX build failed."
}

Write-Host "Built $output"
