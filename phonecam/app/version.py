from __future__ import annotations

import os
import sys
from pathlib import Path


def _read_version_file() -> str | None:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    version_file = base / "assets" / "version.txt"
    if not version_file.exists():
        return None
    value = version_file.read_text(encoding="utf-8").strip()
    return value or None


APP_VERSION = os.environ.get("PHONECAM_VERSION") or _read_version_file() or "0.1.0-dev"
