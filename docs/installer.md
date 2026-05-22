# Installer

PhoneCam uses a WiX MSI for public Windows builds.

The MSI installs:

- `PhoneCam.exe`
- Android companion APK under `assets/`
- driverless camera binaries under `camera/`
- repair/uninstall scripts under `tools/`
- Start Menu shortcut
- `%ProgramData%\PhoneCam`

The MSI does not install a custom Windows driver package. It does not require
Test Mode, unsigned-driver workflows, WDK, Visual Studio, Python, Android Studio,
or Microsoft Hardware Dev Center signing on the user machine.

Build:

```powershell
.\tools\build_driverless_camera.ps1
.\tools\build_android_companion.ps1 -Version v1.0.0-beta.1
cd phonecam
python .\build_tools\build_exe.py
cd ..
.\tools\build_installer.ps1 -Version v1.0.0-beta.1
```

Output:

```text
release/PhoneCam-Setup-v1.0.0-beta.1.msi
```

Repair:

- The app registers or repairs the driverless camera for the current Windows
  user on startup when needed.
- Setup > Repair PhoneCam Camera runs the same driverless repair path.
- The MSI also stages repair scripts for support and uninstall cleanup.

Uninstall:

- Removes installed app files.
- Attempts to unregister the driverless camera.
- Removes PhoneCam runtime frame/stat files from `%ProgramData%\PhoneCam`.

Unsigned beta note:

The public beta can be unsigned. Users may see SmartScreen warnings. Release
assets include SHA256 checksums so users can verify downloads.
