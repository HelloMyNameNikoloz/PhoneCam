# Driver Signing

Public v1 does not require driver signing because the normal camera path is
driverless on Windows 11.

The old UMDF/root-enumerated camera package is experimental and contributor-only.
It may be useful for future Windows 10 research, but it requires WDK tooling and
normal users would need a Microsoft-signed package for Secure Boot systems.

Contributor commands:

```powershell
.\tools\build_native_camera.ps1
.\tools\sign_virtual_camera_test.ps1
.\tools\install_virtual_camera.ps1
```

These commands are not part of public v1. Do not ask public users to enable Test
Mode, disable Secure Boot, install certificates, or run unsigned-driver flows.

App and installer signing is separate. The public beta can be unsigned and
publish SHA256 checksums. Future releases can use SignPath Foundation or another
open-source-friendly signing path.
