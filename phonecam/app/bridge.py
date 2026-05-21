from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from app.config import DEFAULT_SETTINGS
from app.device_detector import DeviceDetector
from app.frame_receiver import FrameReceiver
from app.logger import MemoryLogger
from app.native_settings import write_native_settings
from app.paths import adb_path, companion_apk_path, settings_path
from app.process_utils import run_capture
from app.virtual_camera_status import is_phonecam_installed


class PhoneCamBridge:
    def __init__(self) -> None:
        self.logger = MemoryLogger()
        self.detector = DeviceDetector(adb_path())
        self.receiver = FrameReceiver(self._receiver_log)
        self.settings = self.load_settings()
        write_native_settings(self.settings)
        self.devices: List[Dict[str, str]] = []
        self.device_error: str | None = None
        self._reverse_device: str | None = None
        self._installed_device: str | None = None
        self._companion_device: str | None = None
        self._companion_signature: tuple[str, int, str, str] | None = None
        self._virtual_camera_checked = 0.0
        self._virtual_camera_installed = False
        self.receiver.start()
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

    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**DEFAULT_SETTINGS, **self.settings, **settings}
        self.settings = self._sanitize_settings(merged)
        write_native_settings(self.settings)
        target = settings_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        self.receiver.reset_performance()
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
        self._companion_device = None
        self._ensure_companion_running()

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
            "status": status,
            "error": error or self.device_error,
            "missingAdb": not adb_path().exists(),
            "missingCompanionApk": not companion_apk_path().exists(),
            "missingScrcpy": False,
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

    def _log_device_state(self) -> None:
        if not self.devices:
            self.logger.info("No Android device detected")
            return
        for device in self.devices:
            self.logger.info(f"Device {device['id']} is {device['status']}")

    def _ensure_usb_reverse(self) -> None:
        device = self._selected_ready_device()
        device_id = device["id"] if device else None
        if not device_id:
            self._reverse_device = None
        if not device_id or self._reverse_device == device_id or not adb_path().exists():
            return
        ok = self._reverse_port(device_id, 4767) and self._reverse_port(device_id, 4768)
        if ok:
            self._reverse_device = device_id
            self.logger.success("USB frame tunnels ready for PhoneCam Android companion")

    def _reverse_port(self, device_id: str, port: int) -> bool:
        command = [str(adb_path()), "-s", device_id, "reverse", f"tcp:{port}", f"tcp:{port}"]
        result = run_capture(command, timeout=5)
        if result.returncode == 0:
            return True
        self.logger.warning((result.stderr or f"ADB reverse failed for port {port}").strip())
        return False

    def _ensure_companion_running(self) -> None:
        device = self._selected_ready_device()
        device_id = device["id"] if device else None
        if not device_id:
            self._companion_device = None
            self._companion_signature = None
            return
        signature = (
            device_id,
            int(self.settings.get("fps", 30)),
            str(self.settings.get("resolution", "1920x1080")),
            str(self.settings.get("cameraFacing", "back")),
        )
        if self._companion_signature == signature or not companion_apk_path().exists():
            return
        if self._installed_device != device_id:
            install = run_capture([str(adb_path()), "-s", device_id, "install", "-r", str(companion_apk_path())], timeout=45)
            if install.returncode != 0:
                self.logger.warning((install.stderr or install.stdout or "Companion install failed").strip())
                return
            self._installed_device = device_id
        start = run_capture([
            str(adb_path()),
            "-s",
            device_id,
            "shell",
            "am",
            "start",
            "-n",
            "com.phonecam.companion/.MainActivity",
            "--ei",
            "fps",
            str(int(self.settings.get("fps", 30))),
            "--es",
            "resolution",
            str(self.settings.get("resolution", "1920x1080")),
            "--es",
            "facing",
            str(self.settings.get("cameraFacing", "back")),
        ], timeout=8)
        if start.returncode == 0:
            self._companion_device = device_id
            self._companion_signature = signature
            self.logger.success("PhoneCam Android companion installed and started")
        else:
            self.logger.warning((start.stderr or start.stdout or "Companion start failed").strip())

    def _receiver_log(self, level: str, message: str) -> None:
        getattr(self.logger, level, self.logger.info)(message)

    def _check_virtual_camera_installed(self) -> bool:
        if time.monotonic() - self._virtual_camera_checked < 10:
            return self._virtual_camera_installed
        self._virtual_camera_checked = time.monotonic()
        self._virtual_camera_installed = is_phonecam_installed()
        return self._virtual_camera_installed

    @staticmethod
    def _sanitize_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
        clean = {key: settings.get(key, value) for key, value in DEFAULT_SETTINGS.items()}
        clean["fps"] = int(clean.get("fps", 30))
        return clean
