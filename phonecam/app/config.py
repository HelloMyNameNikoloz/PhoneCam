from __future__ import annotations

APP_NAME = "PhoneCam"
PREVIEW_TITLE = "PhoneCam Preview"
STATUS_POLL_SECONDS = 2

SUPPORTED_RESOLUTIONS = ["1280x720", "1920x1080", "2560x1440", "3840x2160"]
SUPPORTED_FPS = [24, 30, 60, 120]
CAMERA_FACINGS = ["back", "front"]

DEFAULT_SETTINGS = {
    "cameraFacing": "back",
    "resolution": "1920x1080",
    "fps": 30,
    "transportMode": "jpeg",
    "showPreview": True,
    "keepScreenOff": False,
    "selectedDeviceId": None,
    "firstRunComplete": False,
}
