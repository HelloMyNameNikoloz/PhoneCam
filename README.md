# PhoneCam

PhoneCam turns an Android phone into a real selectable Windows camera named
`PhoneCam`. Apps such as OBS, browsers, Discord, Zoom, Teams, and Windows Camera
should be able to choose it from their normal camera dropdown.

PhoneCam is open source under GPLv3. The project goal is simple: high-quality
Android webcam support without watermarks, accounts, cloud services, or
subscription paywalls.

## Status

PhoneCam is currently a working developer build, not a public beta installer.

Working locally:

- Android phone detection over ADB.
- Android companion app auto-install/start over USB.
- Live preview in the PhoneCam desktop app.
- Registered Windows virtual camera named `PhoneCam`.
- OBS receives real frames through the virtual camera.
- Live FPS, latency, dropped-frame, and output diagnostics.

Release blockers:

- Microsoft-signed driver package for Secure Boot users.
- WiX MSI installer with repair/uninstall actions.
- 30-minute 1080p30 soak test on clean Windows 10/11 systems.
- Hot-path performance work to replace JPEG + Python/Pillow.

## Architecture

PhoneCam has four parts:

- `phonecam/`: Python + pywebview Windows control app.
- `android/phonecam-companion/`: Android Camera2 companion app.
- `native/phonecam_virtual_camera/`: Windows Frame Server custom media source
  and UMDF camera registration package.
- `tools/`: build, install, repair, diagnostics, and soak-test scripts.

See:

- `docs/architecture.md`
- `docs/virtual-camera.md`
- `native/phonecam_virtual_camera/FRAME_PIPELINE.md`
- `docs/performance-roadmap.md`
- `docs/driver-signing.md`
- `docs/onboarding.md`
- `docs/test-matrix.md`
- `docs/third-party.md`

## Development Setup

Install:

- Python 3.12+
- Visual Studio Build Tools 2022
- Windows SDK and WDK 10.0.26100+
- Android SDK with platform-tools
- WiX Toolset v4 for MSI work

Python app:

```powershell
cd phonecam
python -m pip install -r requirements.txt
python app/main.py
```

Android companion:

```powershell
.\tools\build_android_companion.ps1
```

Native virtual camera:

```powershell
.\tools\build_native_camera.ps1
```

Release artifacts:

```powershell
.\tools\build_release_artifacts.ps1
```

Local driver development still requires test signing:

```powershell
.\tools\sign_virtual_camera_test.ps1
.\tools\install_virtual_camera.ps1
```

Public releases must use Microsoft driver signing instead of test signing.

## Soak Test

After starting PhoneCam and selecting it in OBS, run:

```powershell
.\tools\run_soak_test.ps1 -Minutes 30
```

The script writes CSV output under `artifacts/soak/`.

## Privacy

PhoneCam is local USB only by default:

- no cloud service
- no account
- no telemetry by default
- no intentional frame recording or screenshot saving

See `docs/privacy.md`.

## Release Plan

The beta release checklist is in `docs/release-checklist.md`.

The installer strategy is in `docs/installer.md`.
