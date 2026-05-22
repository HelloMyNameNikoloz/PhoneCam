param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$releaseDir = Join-Path $root "release\$Version"
$flatRelease = Join-Path $root "release"

function Assert-File($path, $message) {
    if (-not (Test-Path $path)) { throw "$message Missing: $path" }
}

function Write-Checksums($directory, $version) {
    $checksumFile = Join-Path $directory "PhoneCam-$version-checksums.txt"
    Get-ChildItem $directory -File |
        Where-Object { $_.Name -notlike "*checksums.txt" } |
        Sort-Object Name |
        ForEach-Object {
            $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$hash  $($_.Name)"
        } | Set-Content -Path $checksumFile -Encoding ascii
}

function Write-ReleaseNotes($directory, $version) {
    $notes = @"
# PhoneCam $version

Public beta build for Windows 11 and Android.

Assets:
- PhoneCam Windows MSI installer
- PhoneCam Android companion APK
- SHA256 checksums

Known limitations:
- Public v1 targets Windows 11 driverless Media Foundation virtual camera support.
- Windows 10 is experimental and may require future signed-driver work.
- 1080p30 is the stability target. Higher FPS and 4K are best-effort.
- The Windows app and installer are unsigned in the free public beta path, so SmartScreen may warn.
"@
    Set-Content -Path (Join-Path $directory "PhoneCam-$version-release-notes.md") -Value $notes -Encoding utf8
}

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

& (Join-Path $root "tools\build_release_artifacts.ps1") -Version $Version -AndroidOutputDir $releaseDir

$msi = Join-Path $flatRelease "PhoneCam-Setup-$Version.msi"
$apk = Join-Path $releaseDir "PhoneCam-Android-$Version.apk"
Assert-File $msi "Installer build did not produce the expected MSI."
Assert-File $apk "Android build did not produce the expected APK."

Copy-Item -Path $msi -Destination (Join-Path $releaseDir "PhoneCam-Setup-$Version.msi") -Force
Write-ReleaseNotes $releaseDir $Version
Copy-Item -Path (Join-Path $root "docs\release-checklist.md") -Destination (Join-Path $releaseDir "PhoneCam-$Version-known-issues.md") -Force
Write-Checksums $releaseDir $Version

Write-Host "Local release package created: $releaseDir"
