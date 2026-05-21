$ErrorActionPreference = "Stop"

$nativeLog = Join-Path $env:ProgramData "PhoneCam\native_camera.log"
Write-Host "PhoneCam device:"
Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -eq "PhoneCam" } |
    Format-List Status, FriendlyName, InstanceId

Write-Host ""
Write-Host "PhoneCam driver packages:"
pnputil /enum-drivers /class Camera |
    Select-String -Pattern "Published Name|Original Name|Provider Name|Signer Name" -Context 0, 0 |
    Where-Object {
        $_.Line -match "phonecamcameradriver|PhoneCam|Published Name|Signer Name"
    }

Write-Host ""
Write-Host "Frame ports:"
Get-NetTCPConnection -LocalPort 4767, 4768 -ErrorAction SilentlyContinue |
    Select-Object LocalPort, State, OwningProcess,
        @{n = "Process"; e = { (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName } } |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Native camera diagnostics:"
if (Test-Path $nativeLog) {
    Get-Content $nativeLog -Tail 20
} else {
    Write-Host "No native log yet: $nativeLog"
}

$framePath = Join-Path $env:ProgramData "PhoneCam\framebuffer.bin"
if (Test-Path $framePath) {
    $stream = [IO.File]::Open($framePath, "Open", "Read", "ReadWrite")
    try {
        $bytes = New-Object byte[] 40
        [void]$stream.Read($bytes, 0, $bytes.Length)
        $magic = [BitConverter]::ToUInt32($bytes, 0)
        $width = [BitConverter]::ToUInt32($bytes, 8)
        $height = [BitConverter]::ToUInt32($bytes, 12)
        $sequence = [BitConverter]::ToUInt32($bytes, 28)
        Write-Host ""
        Write-Host ("Frame header: magic=0x{0:X8} size={1}x{2} sequence={3}" -f $magic, $width, $height, $sequence)
    } finally {
        $stream.Dispose()
    }
}

$statsPath = Join-Path $env:ProgramData "PhoneCam\native_stats.bin"
if (Test-Path $statsPath) {
    Write-Host ""
    Write-Host "Native stats file: $statsPath ($((Get-Item $statsPath).Length) bytes)"
}

$obsLogDir = Join-Path $env:APPDATA "obs-studio\logs"
if (Test-Path $obsLogDir) {
    $latestObsLog = Get-ChildItem $obsLogDir -Filter *.txt |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    Write-Host ""
    Write-Host "Latest OBS PhoneCam lines: $($latestObsLog.FullName)"
    Select-String -Path $latestObsLog.FullName `
        -Pattern "PhoneCam|DShow Device|fps:|format:|video path|configuration failed|DecodeDeviceId" `
        -CaseSensitive:$false |
        Select-Object -Last 80
}
