<p align="center">
  <img src="assets/icon.png" alt="PhoneCam Logo" width="120" height="120" />
</p>

<h1 align="center">PhoneCam</h1>

<p align="center">
  <strong>Use your Android phone as a real selectable camera on Windows.</strong>
</p>

<p align="center">
  <a href="https://github.com/HelloMyNameNikoloz/PhoneCam/releases/tag/v1.0.0-beta.4"><img src="https://img.shields.io/badge/Version-v1.0.0--beta.4-blue?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-green?style=flat-square" alt="License"></a>
  <a href="docs/windows-support.md"><img src="https://img.shields.io/badge/Platform-Windows%2011-blueviolet?style=flat-square" alt="Platform"></a>
  <a href="android/phonecam-companion"><img src="https://img.shields.io/badge/Android-Companion-orange?style=flat-square" alt="Android Companion"></a>
  <a href="https://github.com/HelloMyNameNikoloz/PhoneCam/releases/tag/v1.0.0-beta.4"><img src="https://img.shields.io/badge/Status-Public%20Beta-yellow?style=flat-square" alt="Status"></a>
</p>

---

PhoneCam is a free and open-source Android-to-Windows virtual camera. It lets you connect your Android phone over USB and select it as a high-quality camera source inside OBS Studio, web browsers, Discord, Zoom, Teams, and other webcam-enabled applications on Windows.

---

### 📥 Downloads (v1.0.0-beta.4)

| Component | File / Asset | Description |
| :--- | :--- | :--- |
| **Windows Installer** | [PhoneCam-Setup-v1.0.0-beta.4.msi](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-Setup-v1.0.0-beta.4.msi) | Install PhoneCam on Windows 11 |
| **Android Companion** | [PhoneCam-Android-v1.0.0-beta.4.apk](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-Android-v1.0.0-beta.4.apk) | Install the companion app on your Android phone |
| **Checksums** | [PhoneCam-v1.0.0-beta.4-checksums.txt](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-v1.0.0-beta.4-checksums.txt) | Verify integrity of downloaded files (SHA-256) |
| **Release Notes** | [v1.0.0-beta.4 Release Notes](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-v1.0.0-beta.4-release-notes.md) | View changes, known issues, and limitations |
| **Source Code** | [ZIP Archive](https://github.com/HelloMyNameNikoloz/PhoneCam/archive/refs/tags/v1.0.0-beta.4.zip) / [TAR.GZ Archive](https://github.com/HelloMyNameNikoloz/PhoneCam/archive/refs/tags/v1.0.0-beta.4.tar.gz) | Download the source code archive |

<details>
<summary>🔑 View File Checksums (SHA-256)</summary>

* **PhoneCam-Android-v1.0.0-beta.4.apk**
  `5d2214a97036a76ac87b3044f74562726335de4c485710cb9676d9757ed6a18c`
* **PhoneCam-Setup-v1.0.0-beta.4.msi**
  `d75f9359eeb1ae4a3c4b6cfe501f0c7f158a9adbfe758bf741a3be31a1c5efe2`
* **PhoneCam-v1.0.0-beta.4-checksums.txt**
  `8c278e1bd5762688105774eca6107f3d877aff8ed6e72abaddf0e2853459a70c`
* **PhoneCam-v1.0.0-beta.4-release-notes.md**
  `0bfd9656e7ab92a75781d3e31e3cb456d72d13d538831d90b39ffd4470cdbca5`

</details>

> [!IMPORTANT]
> **Beta Notice:** This is a public beta. Windows 11 is the fully supported target using the driverless Media Foundation virtual camera path. Windows 10 support is experimental. Because these beta builds are currently unsigned, Windows SmartScreen may show a warning when running the installer.

---

## 🚀 Quick Start

Set up PhoneCam in under 30 seconds:

1. **Install Windows App:** Download and install the [Windows MSI](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-Setup-v1.0.0-beta.4.msi).
2. **Install Android App:** Download and install the [Android APK](https://github.com/HelloMyNameNikoloz/PhoneCam/releases/download/v1.0.0-beta.4/PhoneCam-Android-v1.0.0-beta.4.apk) on your phone.
3. **Launch Windows App:** Open **PhoneCam** on Windows.
4. **Launch Android App:** Open **PhoneCam Companion** on your phone and allow camera permission.
5. **Connect:** Connect your phone to your PC via a USB cable.
6. **Use:** Select **PhoneCam** from the camera dropdown in OBS Studio, your browser, Discord, Zoom, Teams, or any other camera-enabled app.

```text
Android Phone ──(USB)──> PhoneCam Windows App ──> PhoneCam Virtual Camera ──> OBS / Browser / Discord / Zoom / Teams
```

---

## ✨ Features

- **Real Selectable Camera Source:** Registers natively as a system camera named `PhoneCam`.
- **Driverless Virtual Camera Path:** Uses Windows 11 Media Foundation APIs, avoiding legacy custom drivers, Secure Boot issues, and Test Mode requirements.
- **Local-First & Secure:** Camera frames are transported securely over a physical USB connection. No cloud accounts, external servers, or internet access required.
- **Micro-Latency:** High-performance direct pipeline with real-time FPS and transmission statistics.
- **Premium Standard:** Absolutely no watermarks, subscriptions, or intrusive advertisements.
- **Open-Source:** Fully transparent codebase licensed under GPLv3.

---

## 🔌 Compatibility

| Target / App | Status | Notes |
| :--- | :--- | :--- |
| **Windows 11** | Public Beta Target | Fully supported via driverless Media Foundation virtual camera API |
| **Windows 10** | Experimental | Future native virtual camera support is planned/experimental |
| **Android** | Companion APK | Requires Android 8.0+ and camera permissions |
| **OBS Studio** | Intended Target | Works seamlessly as a Video Capture Device |
| **Browser Dropdowns** | Intended Target | Selectable in Chrome, Edge, Firefox, etc. |
| **Discord / Zoom / Teams** | Intended Target | Selectable in all popular conferencing applications |

---

## 🔒 Privacy

PhoneCam is built to be completely private and local-first:

- **Physical Security:** Camera frames travel exclusively over your physical USB cable via secure local `127.0.0.1` tunnels.
- **Zero Cloud Connections:** No cloud servers, login procedures, registration forms, or tracking scripts are included.
- **Untouched Output:** Your hardware camera output is pristine and untouched.

For more details, see the [Privacy Policy](docs/privacy.md).

---

## 🛠️ Troubleshooting

| Problem | What to try |
| :--- | :--- |
| **PhoneCam does not appear in camera lists** | Open PhoneCam on Windows and select `Setup > Repair PhoneCam Camera` |
| **Android phone is not detected** | Reconnect your USB cable, unlock your phone, check developer options, and ensure USB debugging is authorized |
| **Low FPS / Frame drops** | Set resolution to 1080p30, close resource-heavy background apps, and ensure you are using a high-quality USB-3 cable |
| **Windows SmartScreen warnings** | Current public beta builds are unsigned. You can verify the installer's SHA-256 checksum to ensure it is authentic and safe |
| **Wrong or cached application icon** | Reinstall with a clean uninstall, restart Windows Explorer in Task Manager, or reboot to clear the Windows icon cache |
| **Windows 10 support** | Version 1.0.0 targets Windows 11. Windows 10 is currently experimental; please check our docs for driver updates |

For advanced diagnostic assistance, see the full [Troubleshooting Guide](docs/troubleshooting.md).

---

## 💻 Development

Want to compile, inspect, or modify PhoneCam? Here is the list of deeper technical documentation:

* 🏗️ **Architecture Overview:** [architecture.md](docs/architecture.md)
* 📦 **Installer Compilations:** [installer.md](docs/installer.md)
* 🚀 **Release Process & Pipeline:** [release.md](docs/release.md)
* ⚡ **Performance Roadmap:** [performance-roadmap.md](docs/performance-roadmap.md)
* 🧪 **Testing Matrix:** [test-matrix.md](docs/test-matrix.md)
* 📜 **Third-Party Licenses:** [third-party.md](docs/third-party.md)

### Building Locally

Ensure you have Python 3.12+, Visual Studio Build Tools 2022 with Windows SDK, Android SDK, and WiX Toolset. Then run:

```powershell
# 1. Install dependencies
python -m pip install -r phonecam\requirements.txt

# 2. Build the native driverless virtual camera DLL
.\tools\build_driverless_camera.ps1

# 3. Build the Android companion app
.\tools\build_android_companion.ps1 -Version v1.0.0-beta.4

# 4. Compile the Windows PyInstaller executable
cd phonecam
python .\build_tools\build_exe.py
cd ..

# 5. Compile the Windows MSI installer
.\tools\build_installer.ps1 -Version v1.0.0-beta.4
```

---

## 🗺️ Roadmap

- [ ] Improve native video encoding and transport pipeline
- [ ] Stabilize high-frame-rate 1080p60 transmission
- [ ] Expand device compatibility matrix with broad Android device testing
- [ ] Establish a secure, automated build-signing story using open-source code-signing certificates
- [ ] Investigate robust native Virtual Camera support for Windows 10
- [ ] Explore a future iOS companion application

---

## 🤝 Contributing

We welcome your feedback and support! Testing reports, bug reports, compatibility reports, and pull requests are always welcome.

* 📝 Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.
* 🛡️ To report security vulnerabilities, review [SECURITY.md](SECURITY.md).
* 🐛 Encountered an issue? Open a ticket on our [GitHub Issues](https://github.com/HelloMyNameNikoloz/PhoneCam/issues).

---

## 📄 License

PhoneCam is free software licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for the full text.
