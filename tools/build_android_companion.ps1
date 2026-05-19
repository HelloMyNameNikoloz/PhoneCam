param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Project = Join-Path $Root "android\phonecam-companion"
$DefaultSdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"

if (-not $env:ANDROID_HOME -and (Test-Path $DefaultSdk)) {
    $env:ANDROID_HOME = $DefaultSdk
}

if (-not $env:ANDROID_HOME -or -not (Test-Path $env:ANDROID_HOME)) {
    throw "Android SDK not found. Set ANDROID_HOME or install the Android SDK."
}

Push-Location $Project
try {
    gradle :app:assembleDebug
    $Apk = Join-Path $Project "app\build\outputs\apk\debug\app-debug.apk"
    if (-not (Test-Path $Apk)) {
        throw "Build finished but APK was not found at $Apk"
    }
    Write-Host "Built $Apk"

    if ($Install) {
        $Adb = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"
        if (-not (Test-Path $Adb)) {
            throw "adb.exe not found under $env:ANDROID_HOME\platform-tools"
        }
        & $Adb install -r $Apk
    }
}
finally {
    Pop-Location
}
