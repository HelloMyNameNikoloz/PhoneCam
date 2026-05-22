from __future__ import annotations

import os
import sys
from pathlib import Path


def bundled_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def ui_index() -> Path:
    return bundled_root() / "ui" / "index.html"


def asset_path(*parts: str) -> Path:
    return bundled_root() / "assets" / Path(*parts)


def companion_apk_path() -> Path:
    return asset_path("PhoneCamCompanion.apk")


def bin_path(name: str) -> Path:
    return bundled_root() / "bin" / name


def adb_path() -> Path:
    return bin_path("adb.exe")


def scrcpy_path() -> Path:
    return bin_path("scrcpy.exe")


def settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    return base / "PhoneCam" / "settings.json"


def app_data_dir() -> Path:
    return settings_path().parent


def repo_root() -> Path:
    return bundled_root().parent


def tools_dir() -> Path:
    if getattr(sys, "frozen", False):
        return bundled_root() / "tools"
    return repo_root() / "tools"


def repair_script_path() -> Path:
    override = os.environ.get("PHONECAM_REPAIR_SCRIPT")
    if override:
        return Path(override)
    return tools_dir() / "repair_virtual_camera.ps1"
