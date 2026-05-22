param(
    [int]$Minutes = 30,
    [int]$IntervalSeconds = 5,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutputPath) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputPath = Join-Path (Resolve-Path ".") "artifacts\soak\phonecam-soak-$stamp.csv"
}

$outDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

function Read-UInt64($bytes, $offset) {
    if ($bytes.Length -lt ($offset + 8)) { return 0 }
    return [BitConverter]::ToUInt64($bytes, $offset)
}

function Read-Stats {
    $path = Join-Path $env:ProgramData "PhoneCam\native_stats.bin"
    if (-not (Test-Path $path)) { return $null }
    $stream = [IO.File]::Open($path, "Open", "Read", "ReadWrite")
    try {
        $bytes = New-Object byte[] 56
        [void]$stream.Read($bytes, 0, $bytes.Length)
        return [pscustomobject]@{
            OutputFrames = Read-UInt64 $bytes 8
            DuplicateFrames = Read-UInt64 $bytes 16
            LastSequence = Read-UInt64 $bytes 32
            LatencyMs = Read-UInt64 $bytes 40
            Width = [BitConverter]::ToUInt32($bytes, 48)
            Height = [BitConverter]::ToUInt32($bytes, 52)
        }
    } finally {
        $stream.Dispose()
    }
}

"Time,PhoneCamRunning,OutputFrames,DuplicateFrames,LastSequence,LatencyMs,Width,Height,WorkingSetMB,CpuSeconds" |
    Set-Content $OutputPath

$deadline = (Get-Date).AddMinutes($Minutes)
while ((Get-Date) -lt $deadline) {
    $proc = Get-Process PhoneCam -ErrorAction SilentlyContinue | Select-Object -First 1
    $stats = Read-Stats
    $line = [pscustomobject]@{
        Time = (Get-Date).ToString("o")
        PhoneCamRunning = [bool]$proc
        OutputFrames = if ($stats) { $stats.OutputFrames } else { 0 }
        DuplicateFrames = if ($stats) { $stats.DuplicateFrames } else { 0 }
        LastSequence = if ($stats) { $stats.LastSequence } else { 0 }
        LatencyMs = if ($stats) { $stats.LatencyMs } else { 0 }
        Width = if ($stats) { $stats.Width } else { 0 }
        Height = if ($stats) { $stats.Height } else { 0 }
        WorkingSetMB = if ($proc) { [math]::Round($proc.WorkingSet64 / 1MB, 1) } else { 0 }
        CpuSeconds = if ($proc) { [math]::Round($proc.CPU, 1) } else { 0 }
    }
    ($line | ConvertTo-Csv -NoTypeInformation | Select-Object -Skip 1) | Add-Content $OutputPath
    Start-Sleep -Seconds $IntervalSeconds
}

Write-Host "Soak test written to $OutputPath"
