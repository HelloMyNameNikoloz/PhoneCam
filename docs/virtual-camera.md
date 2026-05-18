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
- Installing requires an elevated PowerShell session because `devgen.exe` and `pnputil` register a root-enumerated camera device.

The remaining product work is replacing the sample frame generator with frames decoded from the Android camera stream.

References:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/stream/frame-server-custom-media-source
- https://learn.microsoft.com/en-us/samples/microsoft/windows-driver-samples/simplemediasource-sample/
