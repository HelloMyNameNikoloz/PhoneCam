from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from app.process_utils import run_capture


@dataclass
class DeviceResult:
    devices: List[Dict[str, str]]
    missing_adb: bool = False
    error: str | None = None


class DeviceDetector:
    def __init__(self, adb_exe: Path) -> None:
        self.adb_exe = adb_exe

    def scan(self) -> DeviceResult:
        if not self.adb_exe.exists():
            return DeviceResult([], missing_adb=True, error="Missing adb.exe")

        try:
            result = run_capture([str(self.adb_exe), "devices"])
        except Exception as exc:
            return DeviceResult([], error=f"ADB failed: {exc}")

        if result.returncode != 0:
            return DeviceResult([], error=(result.stderr or "ADB returned an error").strip())

        return DeviceResult(self._parse_devices(result.stdout))

    @staticmethod
    def _parse_devices(output: str) -> List[Dict[str, str]]:
        devices: List[Dict[str, str]] = []
        for raw_line in output.splitlines()[1:]:
            line = raw_line.strip()
            if not line or "\t" not in line:
                continue
            device_id, status = line.split("\t", 1)
            if status not in {"device", "unauthorized", "offline"}:
                continue
            devices.append(
                {
                    "id": device_id,
                    "status": status,
                    "label": "Android Device",
                }
            )
        return devices
