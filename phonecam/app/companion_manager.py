from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Protocol

from app.process_utils import run_capture


class LoggerLike(Protocol):
    def success(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...


class CompanionManager:
    def __init__(self, adb: Path, apk: Path, logger: LoggerLike) -> None:
        self.adb = adb
        self.apk = apk
        self.logger = logger
        self._installed_device: str | None = None
        self._signature: tuple[str, int, str, str, str] | None = None

    def reset(self) -> None:
        self._signature = None

    def ensure_running(self, device_id: str | None, settings: Dict[str, Any]) -> None:
        if not device_id:
            self._signature = None
            return
        signature = self._make_signature(device_id, settings)
        if self._signature == signature or not self.apk.exists():
            return
        if not self._install_if_needed(device_id):
            return
        if self._start(device_id, settings):
            self._signature = signature
            self.logger.success("PhoneCam Android companion installed and started")

    def _make_signature(self, device_id: str, settings: Dict[str, Any]) -> tuple[str, int, str, str, str]:
        return (
            device_id,
            int(settings.get("fps", 30)),
            str(settings.get("resolution", "1920x1080")),
            str(settings.get("cameraFacing", "back")),
            str(settings.get("transportMode", "jpeg")),
        )

    def _install_if_needed(self, device_id: str) -> bool:
        if self._installed_device == device_id:
            return True
        result = run_capture([str(self.adb), "-s", device_id, "install", "-r", str(self.apk)], timeout=45)
        if result.returncode != 0:
            self.logger.warning((result.stderr or result.stdout or "Companion install failed").strip())
            return False
        self._installed_device = device_id
        return True

    def _start(self, device_id: str, settings: Dict[str, Any]) -> bool:
        result = run_capture([
            str(self.adb),
            "-s",
            device_id,
            "shell",
            "am",
            "start",
            "-n",
            "com.phonecam.companion/.MainActivity",
            "--ei",
            "fps",
            str(int(settings.get("fps", 30))),
            "--es",
            "resolution",
            str(settings.get("resolution", "1920x1080")),
            "--es",
            "facing",
            str(settings.get("cameraFacing", "back")),
            "--es",
            "transport",
            str(settings.get("transportMode", "jpeg")),
        ], timeout=8)
        if result.returncode == 0:
            return True
        self.logger.warning((result.stderr or result.stdout or "Companion start failed").strip())
        return False
