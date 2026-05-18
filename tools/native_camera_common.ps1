$ErrorActionPreference = "Stop"

function Get-PhoneCamRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-NativeCameraPackagePath {
    $root = Get-PhoneCamRoot
    return Join-Path $root "native\phonecam_virtual_camera\x64\Release\PhoneCamCameraDriver"
}

function Get-WindowsKitRoot {
    $root = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10"
    if (-not (Test-Path $root)) {
        throw "Windows Kits root was not found at '$root'. Install Windows SDK and WDK."
    }
    return (Resolve-Path $root).Path.TrimEnd("\")
}

function Find-KitBinTool {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Architecture = "x64"
    )

    $binRoot = Join-Path (Get-WindowsKitRoot) "bin"
    $tool = Get-ChildItem $binRoot -Recurse -Filter $Name -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\$Architecture\\$([regex]::Escape($Name))$" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1

    if (-not $tool) {
        throw "$Name was not found under '$binRoot'. Install Windows SDK tools."
    }
    return $tool.FullName
}

function Find-WdkTool {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Architecture = "x64"
    )

    $toolsRoot = Join-Path (Get-WindowsKitRoot) "Tools"
    $tool = Get-ChildItem $toolsRoot -Recurse -Filter $Name -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\$Architecture\\$([regex]::Escape($Name))$" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1

    if (-not $tool) {
        throw "$Name was not found under '$toolsRoot'. Install Windows Driver Kit tools."
    }
    return $tool.FullName
}

function Assert-Elevated {
    param([string]$Action = "perform this operation")

    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Run this script from an elevated PowerShell session to $Action."
    }
}

function Assert-CatalogSigned {
    param([Parameter(Mandatory = $true)][string]$CatalogPath)

    $signtool = Find-KitBinTool -Name "signtool.exe"
    & $signtool verify /pa /q $CatalogPath *> $null
    if ($LASTEXITCODE -ne 0) {
        throw @"
Driver package catalog is unsigned or not trusted:
$CatalogPath

Run these commands from elevated PowerShell:
.\tools\build_native_camera.ps1
.\tools\sign_virtual_camera_test.ps1
bcdedit /set testsigning on

Then reboot Windows and run:
.\tools\install_virtual_camera.ps1
"@
    }
}

function Get-SecureBootState {
    try {
        return [bool](Confirm-SecureBootUEFI -ErrorAction Stop)
    }
    catch {
        return $null
    }
}

function Assert-TestSigningEnabled {
    $bootConfig = bcdedit /enum "{current}" 2>$null | Out-String
    if ($LASTEXITCODE -ne 0 -or $bootConfig -match "(?im)^\s*testsigning\s+Yes\s*$") {
        return
    }

    $secureBoot = Get-SecureBootState
    if ($secureBoot -eq $true) {
        throw @"
Windows test signing is not enabled, and Secure Boot is enabled.

Secure Boot blocks:
bcdedit /set testsigning on

For local development, disable Secure Boot in UEFI/BIOS, boot Windows, run this from elevated PowerShell, then reboot:
bcdedit /set testsigning on

For a production install with Secure Boot enabled, the driver package must be Microsoft signed through attestation or WHQL signing. A local test certificate will not be enough.
"@
    }

    throw "Windows test signing is not enabled. Run 'bcdedit /set testsigning on' from elevated PowerShell, reboot, then run this script again."
}
