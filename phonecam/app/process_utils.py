from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

CREATE_NO_WINDOW = 0x08000000 if sys.platform.startswith("win") else 0


def run_capture(command: List[str], timeout: float = 8) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=CREATE_NO_WINDOW,
    )


def start_process(command: List[str], cwd: Optional[Path] = None) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else None,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )


def terminate_process(process: subprocess.Popen[str], timeout: float = 4) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=timeout)
