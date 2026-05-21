from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.config import SUPPORTED_FPS


def native_settings_path() -> Path:
    return Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "PhoneCam" / "native_settings.txt"


def write_native_settings(settings: dict[str, Any]) -> None:
    fps = _clean_fps(settings.get("fps", 30))
    width, height = _resolution(settings.get("resolution", "1920x1080"))
    path = native_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"fps={fps}\nwidth={width}\nheight={height}\n"
    path.write_text(text, encoding="ascii")


def _clean_fps(value: Any) -> int:
    try:
        fps = int(value)
    except (TypeError, ValueError):
        return 30
    return fps if fps in SUPPORTED_FPS else 30


def _resolution(value: Any) -> tuple[int, int]:
    try:
        width_text, height_text = str(value).lower().split("x", 1)
        width = int(width_text)
        height = int(height_text)
    except (TypeError, ValueError):
        return 1920, 1080
    return width, height
