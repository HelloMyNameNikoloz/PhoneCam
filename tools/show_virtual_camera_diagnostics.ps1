$ErrorActionPreference = "Stop"

$nativeLog = Join-Path $env:ProgramData "PhoneCam\native_camera.log"
Write-Host "PhoneCam device:"
Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -eq "PhoneCam" } |
    Format-List Status, FriendlyName, InstanceId

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
