$ErrorActionPreference = "Stop"

function Find-MSBuild {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
    )
    $msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $msbuild) {
        throw "MSBuild was not found. Install Visual Studio Build Tools 2022 with Desktop development with C++."
    }
    return $msbuild
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$solution = Join-Path $root "native\phonecam_virtual_camera\PhoneCamDriverless.sln"
$outDir = Join-Path $root "native\phonecam_virtual_camera\x64\Release"
$packageDir = Join-Path $root "native\phonecam_virtual_camera\x64\Release\Driverless"

& (Find-MSBuild) $solution /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 /m
if ($LASTEXITCODE -ne 0) { throw "Driverless camera build failed." }

New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
foreach ($file in @("PhoneCamVirtualCamera.dll", "PhoneCamCameraCtl.exe")) {
    $source = Join-Path $outDir $file
    if (-not (Test-Path $source)) { throw "Missing driverless camera output: $source" }
    Copy-Item $source (Join-Path $packageDir $file) -Force
}

Write-Host "Built driverless camera package: $packageDir"
