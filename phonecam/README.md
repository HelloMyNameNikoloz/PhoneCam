# PhoneCam

PhoneCam turns an Android phone into an OBS-ready camera source. The Windows app hosts a local receiver and OBS reads it as a Browser Source, so no separate preview window is required.

When PhoneCam is open it stays available in the Windows system tray and keeps the receiver alive until you quit manually from the tray.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- Android PhoneCam Sender installed on the phone
- Phone and PC on the same private network

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Run in development:

```powershell
python app/main.py
```

## Android Sender

Build and install the sender from the repo root:

```powershell
.\tools\build_android_sender.ps1 -Install
```

Open the Windows app, copy the Android sender URL, paste it into the Android app, and start streaming.

## OBS Setup

1. Open OBS.
2. Add a Browser Source.
3. Set URL to `http://127.0.0.1:4767/obs`.
4. Set size to `1920x1080` for the default stream.
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

- Phone cannot connect: confirm both devices are on the same private network and Windows Firewall allows the receiver.
- Lag: choose `1920x1080` at `30 FPS`.
- Black preview: confirm Android Sender is running and OBS points to `http://127.0.0.1:4767/obs`.
- 4K too heavy: use 1080p30 for best stability. 4K is recommended only when the phone and PC handle it smoothly.

## Notes

PhoneCam does not appear under OBS `Video Capture Device` unless the native signed Windows camera package is installed. The Browser Source path is the no-window OBS integration.
