from __future__ import annotations

import json
from typing import Any, Dict

from app.config import DEFAULT_SETTINGS
from app.paths import settings_path


def sanitize_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    clean = {key: settings.get(key, value) for key, value in DEFAULT_SETTINGS.items()}
    clean["fps"] = int(clean.get("fps", 30))
    return clean


def load_settings() -> Dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_SETTINGS.copy()
    return sanitize_settings({**DEFAULT_SETTINGS, **loaded})


def save_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    clean = sanitize_settings(settings)
    target = settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return clean
