# PhoneCam

PhoneCam turns an Android phone into a clean, low-latency USB camera source for OBS. Version 1 uses ADB and scrcpy camera mode internally. It does not install or emulate a virtual webcam driver.

When PhoneCam is open it stays available in the Windows system tray, starts the camera automatically when an authorized phone is connected, and keeps the `PhoneCam Preview` window available for OBS Window Capture.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- `adb.exe`, `AdbWinApi.dll`, `AdbWinUsbApi.dll`, and `scrcpy.exe` placed in `bin/`
- An Android phone that works with ADB and scrcpy camera mode

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

## OBS Setup

1. Open OBS.
2. Add a Window Capture source.
3. Select `PhoneCam Preview`.
4. Use a separate microphone source, such as Blue Yeti.

PhoneCam will not appear under OBS Video Capture Device in version 1. That list only contains physical cameras and installed virtual webcam drivers. A future version would need a signed Windows virtual camera driver or DirectShow filter to appear there as `PhoneCam`.

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
- Lag: use Stability Mode or choose `1920x1080` at `30 FPS`.
- Black preview: stop the camera, reconnect the phone, and start again. Confirm no other app is using the camera.
- 4K too heavy: use 1080p30 for best stability. 4K is recommended only when the phone and PC handle it smoothly.

## Notes

PhoneCam uses USB only in version 1. Phone audio is disabled by default so OBS can use a dedicated microphone source.
