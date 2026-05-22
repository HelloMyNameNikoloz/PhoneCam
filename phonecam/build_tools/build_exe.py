from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    repo = root.parent
    icon = root / "assets" / "icon.ico"
    companion = root / "assets" / "PhoneCamCompanion.apk"
    add_sep = ";"
    if not companion.exists():
        raise SystemExit("Missing assets/PhoneCamCompanion.apk. Run ..\\tools\\build_android_companion.ps1 first.")
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        "PhoneCam",
        "--add-data",
        f"{root / 'ui'}{add_sep}ui",
        "--add-data",
        f"{root / 'assets'}{add_sep}assets",
        "--add-data",
        f"{root / 'bin'}{add_sep}bin",
        "--add-data",
        f"{repo / 'tools' / 'repair_virtual_camera.ps1'}{add_sep}tools",
        "--add-data",
        f"{repo / 'tools' / 'uninstall_virtual_camera.ps1'}{add_sep}tools",
        "--add-data",
        f"{repo / 'tools' / 'driverless_camera_common.ps1'}{add_sep}tools",
        str(root / "app" / "main.py"),
    ]
    if icon.exists():
        command[6:6] = ["--icon", str(icon)]

    print("Running:", " ".join(f'"{part}"' if " " in part else part for part in command))
    return subprocess.call(command, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
