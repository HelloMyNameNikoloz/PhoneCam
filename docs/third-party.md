# Third-party inventory

This inventory must be checked before every public release.

| Component | Purpose | Location | Release requirement |
| --- | --- | --- | --- |
| pywebview | Windows desktop shell | `phonecam/requirements.txt` | Preserve license in NOTICE |
| PyInstaller | Windows EXE packaging | `phonecam/requirements.txt` | Build-time dependency |
| Android Gradle Plugin | Android companion build | `android/phonecam-companion` | Build-time dependency |
| Android platform-tools / ADB | USB device install and tunnel | `phonecam/bin` or installer runtime | Document version and license |
| scrcpy / FFmpeg / SDL / libusb | Legacy fallback/runtime binaries | `phonecam/bin` | Document exact versions or replace with download script |
| Microsoft Frame Server sample | Native virtual camera base | `native/phonecam_virtual_camera` | Preserve Microsoft notices |
| WIL | Native support library if used by sample | `native/vendor` if present | Preserve license |
| WiX Toolset | MSI packaging | `installer/wix` | Build-time dependency |

Generated APK, EXE, MSI, native build directories, certificates, logs, and local
diagnostic files must not be tracked in git.
