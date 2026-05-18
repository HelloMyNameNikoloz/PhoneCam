from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.camera_runner import CameraRunner
from app.config import DEFAULT_SETTINGS
from app.device_detector import DeviceDetector
from app.logger import MemoryLogger
from app.paths import adb_path, scrcpy_path, settings_path


class PhoneCamBridge:
    def __init__(self) -> None:
        self.logger = MemoryLogger()
        self.detector = DeviceDetector(adb_path())
        self.runner = CameraRunner(scrcpy_path())
        self.settings = self.load_settings()
        self.devices: List[Dict[str, str]] = []
        self.device_error: str | None = None
        self.logger.info("PhoneCam initialized")

    def get_status(self) -> Dict[str, Any]:
        self._handle_disconnected_camera()
        if not self.runner.is_running():
            self._refresh_devices(log_changes=False)
        self._handle_autostart()
        return self._status_payload()

    def refresh_devices(self) -> Dict[str, Any]:
        self._refresh_devices(log_changes=True)
        return self._status_payload()

    def start_camera(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        self.save_settings(settings)
        if self.runner.is_running():
            self.logger.warning("Camera already running")
            return self._status_payload("Camera already running")
        if not self._selected_ready_device():
            self.logger.warning("No authorized Android device available")
            return self._status_payload("Connect and authorize an Android phone first")

        ok, message = self.runner.start(self._settings_for_run())
        (self.logger.success if ok else self.logger.error)(message)
        return self._status_payload(None if ok else message)

    def stop_camera(self) -> Dict[str, Any]:
        stopped = self.runner.stop()
        self.logger.info("Camera stopped" if stopped else "Camera was not running")
        return self._status_payload()

    def get_logs(self) -> List[Dict[str, str]]:
        return self.logger.all()

    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**DEFAULT_SETTINGS, **self.settings, **settings}
        self.settings = self._sanitize_settings(merged)
        target = settings_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        self._restart_if_running()
        return self.settings

    def load_settings(self) -> Dict[str, Any]:
        path = settings_path()
        if not path.exists():
            return DEFAULT_SETTINGS.copy()
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_SETTINGS.copy()
        return self._sanitize_settings({**DEFAULT_SETTINGS, **loaded})

    def shutdown(self) -> None:
        if self.runner.stop():
            self.logger.info("Stopped camera on exit")

    def _refresh_devices(self, log_changes: bool) -> None:
        previous = {(d["id"], d["status"]) for d in self.devices}
        result = self.detector.scan()
        self.devices = result.devices
        self.device_error = result.error
        current = {(d["id"], d["status"]) for d in self.devices}
        if log_changes and result.error:
            self.logger.error(result.error)
        if current != previous:
            self._log_device_state()

    def _handle_disconnected_camera(self) -> None:
        exit_code = self.runner.reap_exit()
        if exit_code not in (None, 0):
            self.logger.error(f"scrcpy exited with code {exit_code}")
            self._refresh_devices(log_changes=False)

    def _handle_autostart(self) -> None:
        if not self.runner.is_running() and self._selected_ready_device():
            ok, message = self.runner.start(self._settings_for_run())
            (self.logger.success if ok else self.logger.error)(message)

    def _restart_if_running(self) -> None:
        if not self.runner.is_running():
            return
        self.runner.stop()
        ok, message = self.runner.start(self._settings_for_run())
        (self.logger.success if ok else self.logger.error)(f"Settings applied: {message}")

    def _selected_ready_device(self) -> Dict[str, str] | None:
        ready = [d for d in self.devices if d["status"] == "device"]
        selected = self.settings.get("selectedDeviceId")
        if selected:
            return next((d for d in ready if d["id"] == selected), None) or (ready[0] if ready else None)
        return ready[0] if ready else None

    def _settings_for_run(self) -> Dict[str, Any]:
        settings = self.settings.copy()
        device = self._selected_ready_device()
        if device:
            settings["selectedDeviceId"] = device["id"]
        return settings

    def _status_payload(self, error: str | None = None) -> Dict[str, Any]:
        status = self._app_status(error)
        return {
            "devices": self.devices,
            "settings": self.settings,
            "cameraRunning": self.runner.is_running(),
            "status": status,
            "error": error or self.device_error,
            "missingAdb": not adb_path().exists(),
            "missingScrcpy": not scrcpy_path().exists(),
            "logs": self.get_logs(),
        }

    def _app_status(self, error: str | None) -> str:
        if error or self.device_error or not adb_path().exists() or not scrcpy_path().exists():
            return "error"
        if self.runner.is_running():
            return "running"
        if any(d["status"] == "device" for d in self.devices):
            return "connected"
        return "waiting"

    def _log_device_state(self) -> None:
        if not self.devices:
            self.logger.info("No Android device detected")
            return
        for device in self.devices:
            self.logger.info(f"Device {device['id']} is {device['status']}")

    @staticmethod
    def _sanitize_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
        clean = {key: settings.get(key, value) for key, value in DEFAULT_SETTINGS.items()}
        clean["fps"] = int(clean.get("fps", 30))
        return clean
