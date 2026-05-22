# Contributing to PhoneCam

PhoneCam aims to be a reliable, free, open-source Android-to-Windows camera.
The bar for changes is practical: stable 1080p30 first, then higher resolutions
and frame rates.

## Development Setup

Required for Windows development:

- Python 3.12+
- Visual Studio Build Tools 2022
- Windows SDK and WDK 10.0.26100+
- Android SDK with platform-tools
- WiX Toolset v4 for MSI packaging

Useful commands:

```powershell
cd phonecam
python -m pip install -r requirements.txt
python app/main.py
```

```powershell
.\tools\build_native_camera.ps1
.\tools\build_android_companion.ps1
```

## Driver Development

Local driver development can use test signing, but public releases must use a
Microsoft-signed driver package. Keep test-signing scripts for contributors only
and do not present them as the normal user install path.

## Pull Request Checklist

- Keep new source files focused and under 200 lines where practical.
- Do not commit generated EXEs, APKs, MSIs, native build outputs, certificates,
  pycache files, logs, or local settings.
- Add or update docs for user-visible behavior.
- Run Python compile checks and any relevant native/Android builds.
- Do not add telemetry, cloud services, accounts, watermarking, or subscriptions.
