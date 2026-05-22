# Architecture

PhoneCam public v1 has four runtime parts.

1. Windows desktop app
   - Python + pywebview UI under `phonecam/`.
   - Detects Android devices with bundled ADB.
   - Opens local USB reverse tunnels to `127.0.0.1`.
   - Receives Android frames, shows preview, writes the latest shared frame, and
     reports real FPS diagnostics.

2. Android companion
   - Camera2 app under `android/phonecam-companion/`.
   - Captures the selected camera at the requested resolution/FPS.
   - Streams frames to the Windows app over the USB tunnel.

3. Driverless Windows 11 virtual camera
   - Native Media Foundation source under `native/phonecam_virtual_camera/`.
   - Registered through `MFCreateVirtualCamera`.
   - Exposes a selectable camera named `PhoneCam` without a custom Windows
     driver package, EV certificate, Hardware Dev Center signing, or Test Mode.

4. Installer and release tooling
   - WiX MSI installs the app, APK, driverless camera binaries, scripts, Start
     Menu shortcut, and ProgramData folder.
   - GitHub Actions builds release assets on version tags.

## Public V1 Path

The public v1 path is:

Android Camera2 -> USB ADB reverse tunnel -> PhoneCam Windows receiver ->
shared latest-frame buffer -> Media Foundation virtual camera source ->
OBS/browsers/meeting apps.

This path is Windows 11 first because the driverless virtual camera API is
available there. Windows 10 support is future work unless a free driverless path
is proven.

## Experimental Legacy Driver Path

The older root-enumerated UMDF camera driver path remains in the repository for
research and contributor experimentation only. It requires WDK tooling and, for
normal Secure Boot users, Microsoft driver signing. Public v1 installers do not
install it and public docs must not ask users to enable Test Mode.

## Frame Contract

The native source reads runtime files under `%ProgramData%\PhoneCam`:

- `framebuffer.bin`: latest live frame.
- `native_settings.txt`: selected resolution and FPS.
- `native_stats.bin`: output FPS, latency, duplicate/drop counters.

The current beta frame path is JPEG capture plus Python decode into BGRA. The
planned production path is YUV/NV12 or hardware video transport with a native
receiver and ring buffer.
