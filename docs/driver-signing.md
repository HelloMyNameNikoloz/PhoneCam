# Driver signing

PhoneCam exposes a Windows camera device through a native camera driver/media
source package. Public releases must use Microsoft signing. Local test signing
is only for contributors.

## Public release path

1. Build the native package with `tools\build_native_camera.ps1`.
2. Validate the package on Windows 10 and Windows 11.
3. Submit the package through Microsoft Partner Center Hardware Dev Center for
   attestation or WHQL signing.
4. Use the Microsoft-signed package in the WiX MSI.
5. Verify installation with Secure Boot enabled.

This is the path normal users need. It avoids asking users to disable Secure
Boot or enable Windows test signing.

## Contributor-only test signing

Local development can use:

```powershell
.\tools\build_native_camera.ps1
.\tools\sign_virtual_camera_test.ps1
.\tools\install_virtual_camera.ps1
```

This requires Windows test signing mode. If Secure Boot is enabled, Windows will
block test signing. Do not document this as the normal user install path.

## Release gate

PhoneCam beta installers must not ship with a locally test-signed driver. The
release checklist should block publication unless the camera package is signed
by Microsoft Windows Hardware Compatibility Publisher.
