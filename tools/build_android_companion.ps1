param(
    [string]$Version = "0.3.0",
    [string]$OutputDir = "",
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
    $versionName = $Version.TrimStart("v")
    $digits = [regex]::Matches($versionName, "\d+") | ForEach-Object { $_.Value }
    $versionCode = if ($digits.Count -gt 0) {
        [int](($digits | Select-Object -First 3) -join "")
    }
    else {
        1
    }

    gradle :app:assembleDebug "-PphonecamVersionName=$versionName" "-PphonecamVersionCode=$versionCode"
    if ($LASTEXITCODE -ne 0) {
        throw "Android companion build failed."
    }
    $Apk = Join-Path $Project "app\build\outputs\apk\debug\app-debug.apk"
    if (-not (Test-Path $Apk)) {
        throw "Build finished but APK was not found at $Apk"
    }
    Write-Host "Built $Apk"
    $AssetApk = Join-Path $Root "phonecam\assets\PhoneCamCompanion.apk"
    Copy-Item -Path $Apk -Destination $AssetApk -Force
    Write-Host "Copied companion APK to $AssetApk"

    if ($OutputDir) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        $NamedApk = Join-Path $OutputDir "PhoneCam-Android-$Version.apk"
        Copy-Item -Path $Apk -Destination $NamedApk -Force
        Write-Host "Copied release APK to $NamedApk"
    }

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
