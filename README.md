# PhoneCam

PhoneCam is now rooted at this directory.

- `phonecam/` contains the Python desktop control app.
- `android/phonecam-companion/` contains the Android Camera2 frame producer.
- `native/phonecam_virtual_camera/` contains the v2 Windows virtual camera package.
- `native/vendor/` contains Microsoft sample code used as the base for the Frame Server camera implementation.
- `tools/` contains build and install helpers.

## V2 Direction

The real camera device path is Windows Frame Server Custom Media Source:

1. A UMDF stub driver registers `PhoneCam` under the Windows camera categories.
2. A COM media source DLL provides frames to Windows camera clients.
3. The Python app receives Android frames over an ADB reverse tunnel.
4. The Android companion captures Camera2 frames and posts them over USB.

Building the native camera requires Visual Studio Build Tools 2022, Windows SDK 10.0.26100, and WDK 10.0.26100.

```powershell
.\tools\build_native_camera.ps1
```

For local development, sign the generated catalog with a local test certificate from an elevated PowerShell session:

```powershell
.\tools\sign_virtual_camera_test.ps1
```

Windows must also allow test-signed drivers. Run this once from elevated PowerShell, then reboot:

```powershell
bcdedit /set testsigning on
```

If Windows reports that the value is protected by Secure Boot policy, disable Secure Boot in UEFI/BIOS first. For production installs with Secure Boot enabled, the driver package must be Microsoft signed through attestation or WHQL signing.

Installing/registering the camera also requires elevated PowerShell:

```powershell
.\tools\install_virtual_camera.ps1
```

Build and install the Android companion:

```powershell
.\tools\build_android_companion.ps1 -Install
```

Run the Windows app:

```powershell
cd phonecam
python app/main.py
```

The app starts a local frame receiver and runs `adb reverse tcp:4767 tcp:4767`.
Open the Android companion and start the camera. Apps should select `PhoneCam`
directly from their normal camera device dropdown.

Check registration and frame-buffer state:

```powershell
.\tools\check_virtual_camera.ps1
```

Current v2 status:

- The native package builds and produces a catalog.
- `tools/sign_virtual_camera_test.ps1` creates/trusts a local test certificate and signs the catalog.
- The INF registers the Windows camera device as `PhoneCam`.
- The media source reads frames from `C:\ProgramData\PhoneCam\framebuffer.bin`.
- The Python app writes decoded Android frames into that frame buffer.
