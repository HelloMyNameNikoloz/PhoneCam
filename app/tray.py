from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Callable


class TrayController:
    def __init__(self, icon_path: Path, on_show: Callable[[], None], on_quit: Callable[[], None]) -> None:
        self.icon_path = icon_path
        self.on_show = on_show
        self.on_quit = on_quit
        self._icon = None
        self._quitting = False
        self._lock = Lock()

    @property
    def quitting(self) -> bool:
        with self._lock:
            return self._quitting

    def start(self) -> None:
        try:
            import pystray
            from PIL import Image
        except Exception:
            return

        image = Image.open(self.icon_path) if self.icon_path.exists() else Image.new("RGB", (64, 64), "#10a37f")
        menu = pystray.Menu(
            pystray.MenuItem("Open PhoneCam", self._show),
            pystray.MenuItem("Quit PhoneCam", self._quit),
        )
        self._icon = pystray.Icon("PhoneCam", image, "PhoneCam", menu)
        self._icon.run_detached()

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()
            self._icon = None

    def _show(self, *_args) -> None:
        self.on_show()

    def _quit(self, *_args) -> None:
        with self._lock:
            self._quitting = True
        self.stop()
        self.on_quit()
