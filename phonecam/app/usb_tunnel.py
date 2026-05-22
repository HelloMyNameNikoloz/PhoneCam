from __future__ import annotations

from pathlib import Path

from app.logger import MemoryLogger
from app.process_utils import run_capture


def ensure_reverse_tunnels(adb: Path, device_id: str | None, current: str | None, logger: MemoryLogger) -> str | None:
    if not device_id:
        return None
    if current == device_id or not adb.exists():
        return current
    ok = _reverse_port(adb, device_id, 4767, logger) and _reverse_port(adb, device_id, 4768, logger)
    if ok:
        logger.success("USB frame tunnels ready for PhoneCam Android companion")
        return device_id
    return current


def _reverse_port(adb: Path, device_id: str, port: int, logger: MemoryLogger) -> bool:
    command = [str(adb), "-s", device_id, "reverse", f"tcp:{port}", f"tcp:{port}"]
    result = run_capture(command, timeout=5)
    if result.returncode == 0:
        return True
    logger.warning((result.stderr or f"ADB reverse failed for port {port}").strip())
    return False
