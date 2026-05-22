from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.process_utils import run_capture


class LoggerLike(Protocol):
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...


def launch_repair(script: Path, logger: LoggerLike) -> str | None:
    if not script.exists():
        message = "PhoneCam repair script is not available in this build"
        logger.warning(message)
        return message
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{script}\"'",
    ]
    result = run_capture(command, timeout=5)
    if result.returncode == 0:
        logger.info("PhoneCam camera repair launched with administrator privileges")
        return None
    message = (result.stderr or result.stdout or "Repair launch failed").strip()
    logger.warning(message)
    return message
