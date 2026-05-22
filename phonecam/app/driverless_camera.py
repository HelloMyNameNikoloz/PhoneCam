from __future__ import annotations

from app.paths import camera_tool_path, media_source_path
from app.process_utils import run_capture


def driverless_camera_available() -> bool:
    return camera_tool_path().exists() and media_source_path().exists()


def run_driverless_camera(action: str) -> tuple[bool, str]:
    if not driverless_camera_available():
        return False, "Driverless PhoneCam camera files are missing."
    result = run_capture([str(camera_tool_path()), action, str(media_source_path())], timeout=15)
    output = (result.stdout or result.stderr or "").strip()
    return result.returncode == 0, output
