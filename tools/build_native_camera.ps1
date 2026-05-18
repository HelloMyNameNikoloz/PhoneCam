$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$solution = Join-Path $root "native\phonecam_virtual_camera\PhoneCamVirtualCamera.sln"
$candidates = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)
$msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $msbuild) {
    throw "MSBuild Build Tools were not found."
}

$sdkRoot = "${env:ProgramFiles(x86)}\Windows Kits\10"
$sdkVersion = "10.0.26100.0"
$wdkBuild = Join-Path $sdkRoot "build\$sdkVersion"

if (-not (Test-Path $wdkBuild)) {
    throw "Windows Driver Kit $sdkVersion was not found. Install WDK 10.0.26100 or newer."
}

$uapProps = Join-Path $sdkRoot "DesignTime\CommonConfiguration\Neutral\UAP\$sdkVersion\UAP.props"
if (-not (Test-Path $uapProps)) {
    throw "Windows SDK $sdkVersion desktop/UAP design-time files were not found."
}

& $msbuild $solution `
    /p:Configuration=Release `
    /p:Platform=x64 `
    /p:PlatformTarget=x64 `
    /p:PlatformToolset=v143 `
    /p:WindowsTargetPlatformVersion=$sdkVersion `
    /p:PhoneCamUseInstalledWdkProps=true `
    "/p:WDKContentRoot=$sdkRoot\" `
    /p:WDKBuildFolder=$sdkVersion `
    /p:SkipPackageVerification=true `
    /m
