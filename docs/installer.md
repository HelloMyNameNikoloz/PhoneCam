# Installer Strategy

PhoneCam will use WiX Toolset v4 for the Windows installer.

The MSI must install:

- `PhoneCam.exe`
- bundled ADB runtime files
- Android companion APK
- Microsoft-signed PhoneCam virtual camera driver package
- Start Menu shortcut
- repair and uninstall actions

The MSI must not require users to disable Secure Boot or enable test signing.
Contributor-only test signing remains documented separately for driver
development.

Planned custom actions:

- Install or repair the PhoneCam camera device.
- Remove the camera device and PhoneCam driver package during uninstall.
- Clear `%ProgramData%\PhoneCam` runtime files during uninstall.

The first WiX project in this repository is a packaging skeleton. It is not a
public-release installer until the driver package is Microsoft-signed. The
current skeleton stages the app, companion APK, and signed driver package files;
driver install/repair custom actions are still a release blocker.

Build the MSI after producing the desktop EXE, Android APK, and native driver:

```powershell
.\tools\build_installer.ps1
```

For public release validation, require a trusted signed catalog:

```powershell
.\tools\build_installer.ps1 -RequireSignedDriver
```

The script bootstraps a project-local WiX CLI under `.tools/wix` if `wix.exe`
is not already available. The MSI is written to `release/`.
