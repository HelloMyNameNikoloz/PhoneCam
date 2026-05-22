param(
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$wix = Get-Command wix.exe -ErrorAction SilentlyContinue
if (-not $wix) {
    throw "WiX Toolset v4 was not found. Install WiX and ensure wix.exe is on PATH."
}

$appExe = Join-Path $root "phonecam\dist\PhoneCam.exe"
$apk = Join-Path $root "phonecam\assets\PhoneCamCompanion.apk"
$driver = Join-Path $root "native\phonecam_virtual_camera\x64\Release\PhoneCamCameraDriver"
$outDir = Join-Path $root "artifacts\installer"

foreach ($required in @($appExe, $apk, $driver)) {
    if (-not (Test-Path $required)) {
        throw "Missing installer input: $required"
    }
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$output = Join-Path $outDir "PhoneCam-$Configuration.msi"

& $wix.Source build `
    (Join-Path $root "installer\wix\PhoneCam.wxs") `
    -d SourceRoot=$root `
    -d AppExe=$appExe `
    -d CompanionApk=$apk `
    -d DriverDir=$driver `
    -o $output

if ($LASTEXITCODE -ne 0) {
    throw "WiX build failed."
}

Write-Host "Built $output"
