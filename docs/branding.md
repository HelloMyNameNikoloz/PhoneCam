# PhoneCam Branding Guidelines & Icons

This document establishes the official branding guidelines for PhoneCam, specifically detailing the application icon assets used across all platforms.

---

## 🎨 Canonical Source Icon

- **Location**: [assets/icon.png](file:///d:/Programming/Random/PhoneCam/assets/icon.png)
- **Description**: The official, high-resolution logo for PhoneCam.
- **Single Source of Truth**: This image is the single source of truth for the PhoneCam brand. **Do not** manually edit or override generated platform-specific assets. If an icon change is required, modify `assets/icon.png` first and regenerate the format assets.

---

## 🚀 Generated Icon Formats

We dynamically compile and export multiple platform-specific variants from `assets/icon.png`:

### 1. Windows App & Installer (`.ico`)
- **Location**: [assets/icon.ico](file:///d:/Programming/Random/PhoneCam/assets/icon.ico)
- **Staging Location**: [phonecam/assets/icon.ico](file:///d:/Programming/Random/PhoneCam/phonecam/assets/icon.ico)
- **Details**: Contains multi-resolution imagery (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256).
- **Use Cases**: PyInstaller executable compile icon, system tray menu icon, WiX setup installer window, Start Menu shortcuts, and Windows Add/Remove Programs.

### 2. Android Mipmap Icons (`.png`)
- **Location**: `android/phonecam-companion/app/src/main/res/`
- **Variants**: Standard square (`ic_launcher.png`) and circular (`ic_launcher_round.png`) across all densities:
  - `mdpi` (48x48)
  - `hdpi` (72x72)
  - `xhdpi` (96x96)
  - `xxhdpi` (144x144)
  - `xxxhdpi` (192x192)

---

## 🔧 How to Regenerate Icons

If you make modifications to the source `assets/icon.png`, you can easily regenerate all required assets for both platforms using our automated PowerShell CLI wrapper:

```powershell
# Run from the repository root
powershell -ExecutionPolicy Bypass -File tools/assets/generate_icons.ps1
```

This CLI script:
1. Validates the existence of the source `assets/icon.png` image.
2. Invokes Python and Pillow to execute standard bilinear/lanczos downsamplings and crops.
3. Automatically writes to Windows and Android asset folders.
4. Validates all generated assets and lists file sizes.
