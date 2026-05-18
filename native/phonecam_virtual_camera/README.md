# PhoneCam Virtual Camera

This directory is the v2 native Windows camera package.

It is based on Microsoft’s `SimpleMediaSource` Frame Server Custom Media Source sample, renamed and organized for PhoneCam. When built and installed, the camera package is intended to register a Windows camera named `PhoneCam`.

Current state:

- UMDF stub driver package shape is present.
- COM media source package shape is present.
- INF friendly name is `PhoneCam`.
- Build requires the Windows Driver Kit toolsets.
- The media source still uses the sample frame generator until the PhoneCam frame bridge is wired in.

Required local tools:

- Visual Studio Build Tools 2022
- Windows 10/11 SDK
- Windows Driver Kit with Visual Studio integration

Build from the repository root:

```powershell
.\tools\build_native_camera.ps1
```

Install from an elevated PowerShell after a successful build:

```powershell
.\tools\install_virtual_camera.ps1
```

Microsoft reference:

- https://learn.microsoft.com/en-us/windows-hardware/drivers/stream/frame-server-custom-media-source
