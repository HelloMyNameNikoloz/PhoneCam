# PhoneCam

PhoneCam turns an Android phone into a registered Windows camera named `PhoneCam`.

When PhoneCam is open it stays available in the Windows system tray, receives frames from the Android companion over USB, and writes those frames to the native virtual camera bridge.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- `adb.exe`, `AdbWinApi.dll`, and `AdbWinUsbApi.dll` placed in `bin/`
- Installed PhoneCam native camera package
- Installed PhoneCam Android companion

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Run in development:

```powershell
python app/main.py
```

## Android Setup

1. Enable Developer Options.
2. Enable USB Debugging.
3. Connect phone via USB.
4. Accept the RSA debugging prompt on the phone.
5. Open the PhoneCam Android companion.

## OBS Setup

1. Open OBS.
2. Add a Video Capture Device source.
3. Select `PhoneCam`.
4. Confirm the app shows Android frames are feeding the virtual camera.
5. Use your microphone as a separate audio source.

## Build PhoneCam.exe

The build script bundles `ui/`, `assets/`, and `bin/` into a windowed PyInstaller app:

```powershell
python build_tools/build_exe.py
```

The output is created at:

```text
dist/PhoneCam.exe
```

## Troubleshooting

- Phone not detected: confirm the cable supports data, USB debugging is enabled, and `adb.exe` is present in `bin/`.
- Unauthorized: unlock your phone and accept the USB debugging prompt.
- Offline: reconnect the cable or switch USB mode to Transferring images / PTP or Charging only.
- Lag: choose `1920x1080` at `30 FPS`.
- PhoneCam not listed: build, sign, and install the native camera package, then restart OBS.
- Black preview: confirm the Android companion is open and PhoneCam reports received frames.
- 4K too heavy: use 1080p30 for best stability. 4K is recommended only when the phone and PC handle it smoothly.

## Notes

PhoneCam uses USB only in the desktop app. Phone audio is disabled by default.
