# Release Checklist

## Repository Hygiene

- No generated EXE, APK, MSI, pycache, native x64/Release outputs, logs, local
  certs, or build directories are tracked.
- `LICENSE`, `NOTICE`, `SECURITY.md`, and `CONTRIBUTING.md` are present.
- Third-party binary versions and licenses are documented.

## Stability Gate

- 1080p30 soak test runs for 30 minutes.
- OBS keeps a live PhoneCam source without black frames.
- Phone unplug/replug recovers without reboot.
- OBS/browser/Windows Camera restart still finds PhoneCam.
- Output FPS remains near target and dropped frames do not grow continuously.

## Installer Gate

- WiX MSI installs PhoneCam on clean Windows 10 and Windows 11.
- Driver package is Microsoft-signed.
- Secure Boot remains enabled.
- Repair action restores missing camera registration.
- Uninstall removes app files, camera device, driver package, and ProgramData
  runtime files.

## Public Beta Artifacts

- MSI installer.
- Android companion APK.
- SHA256 checksums.
- Known issues.
- Test matrix.
- Screenshots for README.
