# Release Checklist

## Repository Hygiene

- No generated EXE, APK, MSI, ZIP, native `x64/`, Android `build/`, Python
  `build/`, Python `dist/`, logs, pycache, local certs, or local paths are
  tracked.
- `LICENSE`, `NOTICE`, `SECURITY.md`, and `CONTRIBUTING.md` are present.
- Third-party licenses are documented.

## Public V1 Architecture

- Windows 11 driverless Media Foundation virtual camera path is documented.
- Normal installer does not install a custom driver package.
- Normal installer does not require Test Mode.
- Normal installer does not require EV certificate or Hardware Dev Center
  signing.
- Legacy driver path is clearly experimental.

## Stability Gate

- 1080p30 soak test runs for 30 minutes.
- OBS keeps a live PhoneCam source without black frames.
- Phone unplug/replug recovers without reboot.
- OBS/browser/Windows Camera restart still finds PhoneCam.
- Output FPS remains near target and dropped frames do not grow continuously.

## Installer Gate

- Clean Windows 11 install works from MSI.
- PhoneCam opens from Start Menu.
- Repair action restores camera registration.
- Uninstall removes app files and runtime files.

## Public Beta Assets

- `PhoneCam-Setup-<version>.msi`
- `PhoneCam-Android-<version>.apk`
- SHA256 checksums
- Release notes
- Known limitations
