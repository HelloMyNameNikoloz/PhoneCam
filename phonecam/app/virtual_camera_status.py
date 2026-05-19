from __future__ import annotations

from app.process_utils import run_capture


def is_phonecam_installed() -> bool:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue | "
        "Where-Object { $_.FriendlyName -eq 'PhoneCam' } | Select-Object -First 1",
    ]
    try:
        result = run_capture(command, timeout=3)
    except Exception:
        return False
    return bool(result.stdout.strip())
