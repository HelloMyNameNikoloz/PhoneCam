# Virtual Camera Notes

PhoneCam v2 must install a real Windows camera source to appear in camera pickers.

The selected architecture is Microsoft Frame Server Custom Media Source. Microsoft documents two required pieces:

- A driver package with a stub driver that registers the camera device interface.
- A COM DLL that hosts the custom media source.

The native package currently starts from Microsoft’s `SimpleMediaSource` sample because it already implements the correct registration and media-source shape.

Current status:

- `tools/build_native_camera.ps1` builds the package with VS Build Tools 2022, Windows SDK 10.0.26100, and WDK 10.0.26100.
- The INF friendly name is `PhoneCam`.
- The package output is `native/phonecam_virtual_camera/x64/Release/PhoneCamCameraDriver/`.
- `tools/sign_virtual_camera_test.ps1` creates a local code-signing certificate, trusts it in LocalMachine Root and TrustedPublisher, signs the generated `.cat`, and verifies it.
- Windows test signing must be enabled for local development with `bcdedit /set testsigning on`, followed by a reboot. Secure Boot blocks test signing; disable Secure Boot for local driver development or use Microsoft attestation/WHQL signing for production installs.
- Installing requires an elevated PowerShell session because `devgen.exe` and `pnputil` register a root-enumerated camera device.
- `tools/install_virtual_camera.ps1` refuses to install when the generated catalog is unsigned or untrusted.
- `PhoneCamCameraDriver` uses the same reference string as the INF: `PhoneCamCameraSource`.
- `PhoneCamVirtualCamera.dll` reads BGRA frames from `C:\ProgramData\PhoneCam\framebuffer.bin`.
- The Python app receives JPEG frames on `127.0.0.1:4767/frame`, decodes them with Pillow, and writes the frame buffer.
- The Android companion posts Camera2 JPEG frames to `127.0.0.1:4767/frame`; the Windows app creates the USB path with `adb reverse tcp:4767 tcp:4767`.

If `PhoneCam` does not appear in OBS, check these in order:

1. `.\tools\build_native_camera.ps1` succeeds.
2. `.\tools\sign_virtual_camera_test.ps1` succeeds from elevated PowerShell.
3. Test signing is enabled and Windows has been rebooted.
4. Secure Boot is disabled for local test-signed driver development.
5. `.\tools\install_virtual_camera.ps1` succeeds from elevated PowerShell.
6. `Get-PnpDevice -Class Camera | Where-Object FriendlyName -eq "PhoneCam"` returns a device.
7. Restart OBS or the browser after installing the camera.

References:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/stream/frame-server-custom-media-source
- https://learn.microsoft.com/en-us/samples/microsoft/windows-driver-samples/simplemediasource-sample/
