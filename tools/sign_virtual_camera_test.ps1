$ErrorActionPreference = "Stop"
. "$PSScriptRoot\native_camera_common.ps1"

Assert-Elevated "create and trust the PhoneCam local test certificate"

$package = Get-NativeCameraPackagePath
$catalog = Join-Path $package "phonecamcameradriver.cat"
if (-not (Test-Path $catalog)) {
    throw "Catalog not found. Run .\tools\build_native_camera.ps1 first."
}

$subject = "CN=PhoneCam Local Test Certificate"
$cert = Get-ChildItem Cert:\LocalMachine\My |
    Where-Object { $_.Subject -eq $subject -and $_.HasPrivateKey -and $_.NotAfter -gt (Get-Date) } |
    Sort-Object NotAfter -Descending |
    Select-Object -First 1

if (-not $cert) {
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject $subject `
        -CertStoreLocation Cert:\LocalMachine\My `
        -KeyExportPolicy Exportable `
        -KeyUsage DigitalSignature `
        -HashAlgorithm SHA256 `
        -KeyLength 2048 `
        -NotAfter (Get-Date).AddYears(5)
}

$certificateFile = Join-Path $env:TEMP "PhoneCamLocalTestCertificate.cer"
Export-Certificate -Cert $cert -FilePath $certificateFile | Out-Null
Import-Certificate -FilePath $certificateFile -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
Import-Certificate -FilePath $certificateFile -CertStoreLocation Cert:\LocalMachine\TrustedPublisher | Out-Null

$signtool = Find-KitBinTool -Name "signtool.exe"
& $signtool sign /v /fd SHA256 /sm /sha1 $cert.Thumbprint $catalog
if ($LASTEXITCODE -ne 0) {
    throw "signtool failed to sign '$catalog'."
}

& $signtool verify /pa /v $catalog
if ($LASTEXITCODE -ne 0) {
    throw "signtool failed to verify '$catalog'."
}

Write-Host "Signed and verified: $catalog"
$secureBoot = Get-SecureBootState
if ($secureBoot -eq $true) {
    Write-Host "Secure Boot is enabled. Disable Secure Boot in UEFI/BIOS before enabling Windows test signing."
}
Write-Host "For local driver loading, enable Windows test signing from elevated PowerShell and reboot:"
Write-Host "bcdedit /set testsigning on"
