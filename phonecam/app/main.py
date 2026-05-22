from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Redirect stdout/stderr in windowed mode to prevent NoneType write crashes and capture logs
if sys.stdout is None or sys.stderr is None:
    import os
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    log_dir = base / "PhoneCam"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    class LogWriter:
        def __init__(self, filepath: Path):
            self.filepath = filepath

        def write(self, message: str):
            if message:
                try:
                    with self.filepath.open("a", encoding="utf-8") as f:
                        f.write(message)
                except Exception:
                    pass

        def flush(self):
            pass

    if sys.stdout is None:
        sys.stdout = LogWriter(log_dir / "stdout.log")
    if sys.stderr is None:
        sys.stderr = LogWriter(log_dir / "stderr.log")

import webview

from app.bridge import PhoneCamBridge
from app.config import APP_NAME
from app.paths import asset_path, ui_index
from app.single_instance import SingleInstance
from app.tray import TrayController


def main() -> None:
    instance = SingleInstance()
    if not instance.acquire():
        return

    bridge = PhoneCamBridge()
    tray: TrayController | None = None

    window = webview.create_window(
        APP_NAME,
        url=ui_index().as_uri(),
        js_api=bridge,
        width=1100,
        height=720,
        min_size=(940, 640),
        background_color="#0f1014",
    )

    def show_window() -> None:
        window.show()
        window.restore()

    def quit_app() -> None:
        bridge.shutdown()
        window.destroy()

    tray = TrayController(asset_path("icon.ico"), show_window, quit_app)

    def handle_closing() -> bool:
        if tray and tray.quitting:
            bridge.shutdown()
            return True
        window.hide()
        bridge.logger.info("PhoneCam hidden to system tray")
        return False

    def handle_closed() -> None:
        if tray:
            tray.stop()
        bridge.shutdown()

    window.events.closing += handle_closing
    window.events.closed += handle_closed
    tray.start()
    webview.start(debug=False)


if __name__ == "__main__":
    main()
