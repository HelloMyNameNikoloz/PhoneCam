# Virtual Camera

## Public V1

PhoneCam public v1 uses the Windows 11 Media Foundation driverless virtual
camera API. The native helper registers a COM media source and calls
`MFCreateVirtualCamera` so apps can select a camera named `PhoneCam`.

Build:

```powershell
.\tools\build_driverless_camera.ps1
```

Repair/register:

```powershell
.\tools\repair_virtual_camera.ps1
```

Unregister:

```powershell
.\tools\uninstall_virtual_camera.ps1
```

The public v1 path does not require:

- custom Windows driver package
- EV certificate
- Microsoft Hardware Dev Center driver signing
- Windows Test Mode
- disabled Secure Boot

## Experimental Legacy Driver Path

The repository still contains an older root-enumerated UMDF camera driver
experiment. It is useful for research and possible Windows 10 support, but it is
not part of the public v1 installer.

Legacy driver scripts such as `build_native_camera.ps1`,
`sign_virtual_camera_test.ps1`, and `install_virtual_camera.ps1` are
contributor-only. Do not direct public v1 users to run them.

## Runtime Frame Source

The media source reads PhoneCam runtime files under `%ProgramData%\PhoneCam` and
serves the latest frame to camera clients. The app tracks capture, bridge, and
output FPS so the UI reports actual performance instead of the selected target
alone.
