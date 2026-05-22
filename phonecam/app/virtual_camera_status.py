from __future__ import annotations

from app.driverless_camera import driverless_camera_available, run_driverless_camera
from app.process_utils import run_capture


def is_phonecam_installed() -> bool:
    if driverless_camera_available():
        ok, _ = run_driverless_camera("status")
        if not ok:
            return False
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
