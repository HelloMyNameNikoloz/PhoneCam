from __future__ import annotations

import time
from typing import Any, Dict, List

from app.companion_manager import CompanionManager
from app.config import DEFAULT_SETTINGS
from app.device_detector import DeviceDetector
from app.driverless_camera import run_driverless_camera
from app.frame_receiver import FrameReceiver
from app.logger import MemoryLogger
from app.native_settings import write_native_settings
from app.paths import adb_path, companion_apk_path
from app.settings_store import load_settings, save_settings
from app.usb_tunnel import ensure_reverse_tunnels
from app.virtual_camera_status import is_phonecam_installed
from app.version import APP_VERSION


class PhoneCamBridge:
    def __init__(self) -> None:
        self.logger = MemoryLogger()
        self.detector = DeviceDetector(adb_path())
        self.receiver = FrameReceiver(self._receiver_log)
        self.companion = CompanionManager(adb_path(), companion_apk_path(), self.logger)
        self.settings = load_settings()
        write_native_settings(self.settings)
        self.devices: List[Dict[str, str]] = []
        self.device_error: str | None = None
        self._reverse_device: str | None = None
        self._virtual_camera_checked = 0.0
        self._virtual_camera_installed = False
        self.receiver.start()
        self._ensure_virtual_camera_registered()
        self.logger.info("PhoneCam initialized")

    def get_status(self) -> Dict[str, Any]:
        self._refresh_devices(log_changes=False)
        return self._status_payload()

    def refresh_devices(self) -> Dict[str, Any]:
        self._refresh_devices(log_changes=True)
        return self._status_payload()

    def start_camera(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        self.save_settings(settings)
        if not self._selected_ready_device():
            self.logger.warning("No authorized Android device available")
            return self._status_payload("Connect and authorize an Android phone first")
        self.receiver.start()
        self._ensure_usb_reverse()
        return self._status_payload()

    def stop_camera(self) -> Dict[str, Any]:
        self.receiver.stop()
        self.logger.info("Frame receiver stopped")
        return self._status_payload()

    def get_logs(self) -> List[Dict[str, str]]:
        return self.logger.all()

    def repair_virtual_camera(self) -> Dict[str, Any]:
        ok, message = run_driverless_camera("repair")
        if ok:
            self._virtual_camera_checked = 0
            self.logger.success("PhoneCam camera registered for this Windows user")
            return self._status_payload()
        self.logger.error(message)
        return self._status_payload(message)

    def register_virtual_camera(self) -> Dict[str, Any]:
        return self.repair_virtual_camera()

    def unregister_virtual_camera(self) -> Dict[str, Any]:
        ok, message = run_driverless_camera("unregister")
        self._virtual_camera_checked = 0
        if ok:
            self.logger.info("PhoneCam camera unregistered for this Windows user")
            return self._status_payload()
        return self._status_payload(message)

    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**DEFAULT_SETTINGS, **self.settings, **settings}
        self.settings = save_settings(merged)
        write_native_settings(self.settings)
        self.receiver.reset_performance()
        self._restart_if_running()
        return self.settings

    def load_settings(self) -> Dict[str, Any]:
        return load_settings()

    def shutdown(self) -> None:
        self.receiver.stop()

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
        self._ensure_usb_reverse()
        self._ensure_companion_running()

    def _restart_if_running(self) -> None:
        self._ensure_usb_reverse()
        self.companion.reset()
        self._ensure_companion_running()

    def _ensure_virtual_camera_registered(self) -> None:
        if is_phonecam_installed():
            self._virtual_camera_installed = True
            self._virtual_camera_checked = time.monotonic()
            return
        ok, message = run_driverless_camera("repair")
        if ok:
            self._virtual_camera_installed = True
            self._virtual_camera_checked = time.monotonic()
            self.logger.success("PhoneCam camera registered for this Windows user")
        else:
            self.logger.warning(message)

    def _selected_ready_device(self) -> Dict[str, str] | None:
        ready = [d for d in self.devices if d["status"] == "device"]
        selected = self.settings.get("selectedDeviceId")
        if selected:
            return next((d for d in ready if d["id"] == selected), None) or (ready[0] if ready else None)
        return ready[0] if ready else None

    def _status_payload(self, error: str | None = None) -> Dict[str, Any]:
        receiver_status = self.receiver.status()
        status = self._app_status(error)
        return {
            "devices": self.devices,
            "settings": self.settings,
            "cameraRunning": receiver_status["framesReceived"] > 0,
            "frameReceiver": receiver_status,
            "performance": self.receiver.performance(int(self.settings.get("fps", 30))),
            "virtualCameraInstalled": self._check_virtual_camera_installed(),
            "virtualCameraStatus": self._virtual_camera_status(receiver_status),
            "status": status,
            "error": error or self.device_error,
            "missingAdb": not adb_path().exists(),
            "missingCompanionApk": not companion_apk_path().exists(),
            "missingScrcpy": False,
            "version": APP_VERSION,
            "logs": self.get_logs(),
        }

    def _app_status(self, error: str | None) -> str:
        if error or self.device_error or not adb_path().exists():
            return "error"
        if self.receiver.status()["framesReceived"] > 0:
            return "running"
        if any(d["status"] == "device" for d in self.devices):
            return "connected"
        return "waiting"

    def _virtual_camera_status(self, receiver_status: Dict[str, Any]) -> str:
        if not self._check_virtual_camera_installed():
            return "missing"
        if self.device_error:
            return "error"
        if receiver_status["framesReceived"] > 0:
            return "active"
        return "no_frames"

    def _log_device_state(self) -> None:
        if not self.devices:
            self.logger.info("No Android device detected")
            return
        for device in self.devices:
            self.logger.info(f"Device {device['id']} is {device['status']}")

    def _ensure_usb_reverse(self) -> None:
        device = self._selected_ready_device()
        device_id = device["id"] if device else None
        self._reverse_device = ensure_reverse_tunnels(adb_path(), device_id, self._reverse_device, self.logger)

    def _ensure_companion_running(self) -> None:
        device = self._selected_ready_device()
        device_id = device["id"] if device else None
        self.companion.ensure_running(device_id, self.settings)

    def _receiver_log(self, level: str, message: str) -> None:
        getattr(self.logger, level, self.logger.info)(message)

    def _check_virtual_camera_installed(self) -> bool:
        if time.monotonic() - self._virtual_camera_checked < 10:
            return self._virtual_camera_installed
        self._virtual_camera_checked = time.monotonic()
        self._virtual_camera_installed = is_phonecam_installed()
        return self._virtual_camera_installed
