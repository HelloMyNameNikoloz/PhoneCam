from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    icon = root / "assets" / "icon.ico"
    add_sep = ";"
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
        str(root / "app" / "main.py"),
    ]
    if icon.exists():
        command[6:6] = ["--icon", str(icon)]

    print("Running:", " ".join(f'"{part}"' if " " in part else part for part in command))
    return subprocess.call(command, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
