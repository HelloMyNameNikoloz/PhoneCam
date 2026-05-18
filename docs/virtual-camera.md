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

The remaining product work is replacing the sample frame generator with frames decoded from the Android camera stream.

References:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/stream/frame-server-custom-media-source
- https://learn.microsoft.com/en-us/samples/microsoft/windows-driver-samples/simplemediasource-sample/
