# PhoneCam Virtual Camera

This directory is the v2 native Windows camera package.

It is based on Microsoft’s `SimpleMediaSource` Frame Server Custom Media Source sample, renamed and organized for PhoneCam. When built and installed, the camera package is intended to register a Windows camera named `PhoneCam`.

Current state:

- UMDF stub driver package shape is present.
- COM media source package shape is present.
- INF friendly name is `PhoneCam`.
- `tools/build_native_camera.ps1` builds successfully with VS Build Tools 2022, Windows SDK 10.0.26100, and WDK 10.0.26100.
- The media source still uses the sample frame generator until the PhoneCam frame bridge is wired in.

Required local tools:

- Visual Studio Build Tools 2022
- Windows SDK 10.0.26100
- Windows Driver Kit 10.0.26100

Build from the repository root:

```powershell
.\tools\build_native_camera.ps1
```

Sign from elevated PowerShell after a successful build:

```powershell
.\tools\sign_virtual_camera_test.ps1
```

Enable Windows test signing once, then reboot:

```powershell
bcdedit /set testsigning on
```

Secure Boot blocks Windows test signing. Disable Secure Boot for local development, or use Microsoft attestation/WHQL signing for production installs.

Install from elevated PowerShell after signing:

```powershell
.\tools\install_virtual_camera.ps1
```

Microsoft reference:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/stream/frame-server-custom-media-source
