from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import webview

from app.bridge import PhoneCamBridge
from app.config import APP_NAME
from app.paths import asset_path, ui_index
from app.tray import TrayController


def main() -> None:
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

    tray = TrayController(asset_path("logo.png"), show_window, quit_app)

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
