# PhoneCam

PhoneCam is a free, open-source Android-to-Windows camera system. It lets you
connect an Android phone over USB and select `PhoneCam` as a normal camera in
OBS, browsers, Discord, Zoom, Teams, Windows Camera, and other webcam apps.

No watermark. No subscription. No account. No cloud service.

## Public Beta Status

Public v1 targets Windows 11 using the driverless Media Foundation virtual
camera path. The normal installer does not install a custom Windows driver, does
not require Test Mode, and does not require an EV certificate or Microsoft
Hardware Dev Center signing.

Windows 10 is experimental for now. PhoneCam will show a clear unsupported
message when the driverless camera API is unavailable.

## Install

1. Download the latest release from GitHub Releases.
2. Install `PhoneCam-Setup-<version>.msi`.
3. Install `PhoneCam-Android-<version>.apk` on your Android phone.
4. Open PhoneCam on Windows.
5. Connect the phone by USB and accept the Android USB debugging prompt.
6. Allow camera permission in PhoneCam Companion.
7. Select `PhoneCam` in your video app.

The Windows app can also install and launch the companion app over ADB when USB
debugging is enabled.

## OBS Setup

1. Open OBS.
2. Add `Video Capture Device`.
3. Choose `PhoneCam`.
4. Use `Device Default` first.
5. Use a separate microphone source for audio.

## Browser Setup

Open a camera test page or meeting app and choose `PhoneCam` from the browser
camera picker. If it does not appear, open PhoneCam and use Setup > Repair
PhoneCam Camera.

## Development

Requirements:

- Python 3.12+
- Visual Studio Build Tools 2022 with Windows SDK
- Android SDK with platform-tools
- Gradle
- WiX Toolset, or .NET SDK so the build script can install WiX locally

Build locally:

```powershell
python -m pip install -r phonecam\requirements.txt
.\tools\build_driverless_camera.ps1
.\tools\build_android_companion.ps1 -Version v1.0.0-beta.1
cd phonecam
python .\build_tools\build_exe.py
cd ..
.\tools\build_installer.ps1 -Version v1.0.0-beta.1
```

Create a full local release package:

```powershell
powershell -ExecutionPolicy Bypass -File tools\release\create_local_release_package.ps1 -Version v1.0.0-beta.1
```

## Privacy

PhoneCam is local-first:

- frames travel over USB through local `127.0.0.1` tunnels
- no cloud upload
- no telemetry by default
- no frame saving unless explicitly added for diagnostics
- logs must not contain frame data

See `docs/privacy.md`.

## Docs

- `docs/architecture.md`
- `docs/windows-support.md`
- `docs/onboarding.md`
- `docs/installer.md`
- `docs/troubleshooting.md`
- `docs/performance-roadmap.md`
- `docs/release.md`
- `docs/test-matrix.md`
- `docs/third-party.md`

## How To Publish A Release

1. Commit all changes.
2. Push main:

```powershell
git push origin main
```

3. Create a version tag:

```powershell
git tag v1.0.0-beta.1
```

4. Push the tag:

```powershell
git push origin v1.0.0-beta.1
```

GitHub Actions will build the Windows installer, Android APK, checksums, release
notes, and GitHub Release assets automatically.

One-line form:

```powershell
git push origin main; git tag v1.0.0-beta.1; git push origin v1.0.0-beta.1
```
