# PowerShell CLI wrapper for PhoneCam Icon Generation
$ErrorActionPreference = "Stop"

# 1. Resolve paths relative to the script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..\..")

$SourcePng = Join-Path $Root "assets\icon.png"
$IcoFile = Join-Path $Root "assets\icon.ico"
$AppIcoFile = Join-Path $Root "phonecam\assets\icon.ico"
$AndroidRes = Join-Path $Root "android\phonecam-companion\app\src\main\res"

Write-Host "=== PhoneCam Icon Generation CLI ==="

# 2. Assert source icon existence
if (-not (Test-Path $SourcePng)) {
    Write-Error "Source icon not found at expected path: $SourcePng"
    exit 1
}

# 3. Locate Python executable
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    Write-Error "Python was not found in the system PATH. Please install Python 3.12+."
    exit 1
}

Write-Host "Source icon found: $SourcePng"
Write-Host "Executing Python icon generation script..."

# 4. Execute generator
$PyScript = Join-Path $ScriptDir "generate_icons.py"
& $($Python.Source) $PyScript
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python icon generation failed."
    exit 1
}

# 5. Validate the generated assets
Write-Host "Validating generated icon assets..."

$RequiredFiles = @(
    $IcoFile,
    $AppIcoFile,
    (Join-Path $AndroidRes "mipmap-mdpi\ic_launcher.png"),
    (Join-Path $AndroidRes "mipmap-mdpi\ic_launcher_round.png"),
    (Join-Path $AndroidRes "mipmap-hdpi\ic_launcher.png"),
    (Join-Path $AndroidRes "mipmap-hdpi\ic_launcher_round.png"),
    (Join-Path $AndroidRes "mipmap-xhdpi\ic_launcher.png"),
    (Join-Path $AndroidRes "mipmap-xhdpi\ic_launcher_round.png"),
    (Join-Path $AndroidRes "mipmap-xxhdpi\ic_launcher.png"),
    (Join-Path $AndroidRes "mipmap-xxhdpi\ic_launcher_round.png"),
    (Join-Path $AndroidRes "mipmap-xxxhdpi\ic_launcher.png"),
    (Join-Path $AndroidRes "mipmap-xxxhdpi\ic_launcher_round.png")
)

$AllValid = $true
foreach ($File in $RequiredFiles) {
    if (-not (Test-Path $File)) {
        Write-Warning "Missing generated asset: $File"
        $AllValid = $false
    } else {
        $Size = (Get-Item $File).Length
        Write-Host "  [OK] $File ($Size bytes)"
    }
}

if (-not $AllValid) {
    Write-Error "Validation failed. Some generated icons are missing."
    exit 1
}

Write-Host "Validation succeeded! All generated icons are present and valid."
