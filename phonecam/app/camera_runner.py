from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.config import PREVIEW_TITLE
from app.process_utils import start_process, terminate_process


class CameraRunner:
    def __init__(self, scrcpy_exe: Path) -> None:
        self.scrcpy_exe = scrcpy_exe
        self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def return_code(self) -> int | None:
        if self._process is None:
            return None
        return self._process.poll()

    def reap_exit(self) -> int | None:
        if self._process is None:
            return None
        code = self._process.poll()
        if code is None:
            return None
        self._process.wait(timeout=0)
        self._process = None
        return code

    def build_command(self, settings: Dict[str, Any]) -> List[str]:
        command = [
            str(self.scrcpy_exe),
            "--video-source=camera",
            f"--camera-facing={settings.get('cameraFacing', 'back')}",
            f"--camera-size={settings.get('resolution', '1920x1080')}",
            f"--camera-fps={int(settings.get('fps', 30))}",
            "--no-audio",
            f"--window-title={PREVIEW_TITLE}",
        ]
        device_id = settings.get("selectedDeviceId")
        if device_id:
            command.extend(["-s", str(device_id)])
        if settings.get("alwaysOnTop"):
            command.append("--always-on-top")
        if settings.get("keepScreenOff"):
            command.append("--turn-screen-off")
        return command

    def start(self, settings: Dict[str, Any]) -> tuple[bool, str]:
        if self.is_running():
            return False, "Camera already running"
        if not self.scrcpy_exe.exists():
            return False, "Missing scrcpy.exe"

        command = self.build_command(settings)
        try:
            self._process = start_process(command, cwd=self.scrcpy_exe.parent)
        except Exception as exc:
            self._process = None
            return False, f"scrcpy failed to start: {exc}"
        return True, "Camera started"

    def stop(self) -> bool:
        if self._process is None:
            return False
        terminate_process(self._process)
        self._process = None
        return True
