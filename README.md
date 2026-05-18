# PhoneCam

PhoneCam is now rooted at this directory.

- `phonecam/` contains the Python desktop control app.
- `native/phonecam_virtual_camera/` contains the v2 Windows virtual camera package.
- `native/vendor/` contains Microsoft sample code used as the base for the Frame Server camera implementation.
- `tools/` contains build and install helpers.

## V2 Direction

The fast v2 path is an Android sender plus a Windows receiver:

1. The Windows PhoneCam app opens a local receiver on port `4767`.
2. The Android PhoneCam Sender captures the phone camera and posts JPEG frames to the receiver.
3. OBS uses a Browser Source pointed at `http://127.0.0.1:4767/obs`.

This avoids Window Capture and avoids a separate scrcpy preview window. It does not make PhoneCam appear under OBS `Video Capture Device > Device`; Windows requires a signed camera driver/media source for that.

Build the Android sender:

```powershell
.\tools\build_android_sender.ps1
```

Install it to a connected Android phone:

```powershell
.\tools\build_android_sender.ps1 -Install
```

Run the Windows app, copy the Android sender URL shown in the preview area, paste it into the Android app, and start streaming. In OBS, add a Browser Source with:

```text
http://127.0.0.1:4767/obs
```

If the phone cannot reach the Windows receiver, allow PhoneCam/Python through Windows Firewall on the private network.

## Native Camera Device Track

The real camera device path is Windows Frame Server Custom Media Source:

1. A UMDF stub driver registers `PhoneCam` under the Windows camera categories.
2. A COM media source DLL provides frames to Windows camera clients.
3. The Python app remains the control surface for Android detection and capture settings.

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

Current v2 status:

- The native package builds and produces a catalog.
- `tools/sign_virtual_camera_test.ps1` creates/trusts a local test certificate and signs the catalog.
- The INF registers the Windows camera device as `PhoneCam`.
- The media source still uses the sample frame generator until the Android frame bridge is wired in.
