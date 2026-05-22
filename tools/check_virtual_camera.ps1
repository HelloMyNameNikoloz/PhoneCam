$ErrorActionPreference = "Stop"

$camera = Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -eq "PhoneCam" } |
    Select-Object -First 1

if ($camera) {
    Write-Host "PhoneCam camera device is registered:"
    $camera | Format-List Status,Class,FriendlyName,InstanceId
} else {
    Write-Host "PhoneCam camera device is not registered."
    Write-Host "Repair the Windows 11 driverless camera registration:"
    Write-Host ".\tools\repair_virtual_camera.ps1"
}

$framePath = Join-Path $env:ProgramData "PhoneCam\framebuffer.bin"
if (Test-Path $framePath) {
    $item = Get-Item $framePath
    Write-Host "Frame buffer exists: $($item.FullName) ($($item.Length) bytes)"
    $stream = [IO.File]::Open($framePath, "Open", "Read", "ReadWrite")
    try {
        $bytes = New-Object byte[] 40
        [void]$stream.Read($bytes, 0, $bytes.Length)
        $magic = [BitConverter]::ToUInt32($bytes, 0)
        $width = [BitConverter]::ToUInt32($bytes, 8)
        $height = [BitConverter]::ToUInt32($bytes, 12)
        $sequence = [BitConverter]::ToUInt32($bytes, 28)
        Write-Host ("Frame header: magic=0x{0:X8} size={1}x{2} sequence={3}" -f $magic, $width, $height, $sequence)
    } finally {
        $stream.Dispose()
    }
} else {
    Write-Host "Frame buffer not found yet: $framePath"
}
