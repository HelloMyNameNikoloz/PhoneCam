param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$errors = New-Object System.Collections.Generic.List[string]

function Require-File($relative) {
    $path = Join-Path $root $relative
    if (-not (Test-Path $path)) {
        $script:errors.Add("Missing required file: $relative")
    }
}

function Require-Text($relative, $pattern, $message) {
    $path = Join-Path $root $relative
    if (-not (Test-Path $path)) {
        $script:errors.Add("Missing required file: $relative")
        return
    }
    $text = Get-Content $path -Raw
    if ($text -notmatch $pattern) {
        $script:errors.Add($message)
    }
}

if ($Version -notmatch "^v?\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$") {
    $errors.Add("Version must look like v1.0.0-beta.1 or 1.0.0.")
}

foreach ($file in @(
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "README.md",
    "docs\architecture.md",
    "docs\privacy.md",
    "docs\installer.md",
    "docs\release.md",
    "docs\windows-support.md",
    ".github\workflows\release.yml"
)) {
    Require-File $file
}

Require-Text "README.md" "GitHub Releases" "README must link users to GitHub Releases."
Require-Text "docs\architecture.md" "driverless" "Architecture docs must explain the driverless public v1 path."
Require-Text "docs\windows-support.md" "Windows 11" "Windows 11 public v1 support must be documented."
Require-Text "docs\windows-support.md" "Windows 10" "Windows 10 limitation must be documented."

if (-not $SkipBuild) {
    & (Join-Path $root "tools\release\create_local_release_package.ps1") -Version $Version
}

if (-not $SkipBuild) {
    $releaseDir = Join-Path $root "release\$Version"
    foreach ($asset in @(
        "PhoneCam-Setup-$Version.msi",
        "PhoneCam-Android-$Version.apk",
        "PhoneCam-$Version-checksums.txt",
        "PhoneCam-$Version-release-notes.md"
    )) {
        if (-not (Test-Path (Join-Path $releaseDir $asset))) {
            $errors.Add("Missing release artifact: release\$Version\$asset")
        }
    }
}

$trackedGenerated = git -C $root ls-files "*.apk" "*.msi" "*.zip" "phonecam/dist/*" "phonecam/build/*" "native/**/x64/*" 2>$null
if ($trackedGenerated) {
    $errors.Add("Generated binaries are tracked by git:`n$trackedGenerated")
}

$oldErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$diffCheck = & git -C $root diff --check 2>&1
$diffExit = $LASTEXITCODE
$ErrorActionPreference = $oldErrorAction
if ($diffExit -ne 0) {
    $errors.Add("git diff --check failed:`n$diffCheck")
}

if ($errors.Count -gt 0) {
    Write-Host "PUBLISH NOT READY" -ForegroundColor Red
    foreach ($item in $errors) {
        Write-Host "- $item" -ForegroundColor Red
    }
    exit 1
}

Write-Host "PUBLISH READY" -ForegroundColor Green
