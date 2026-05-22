# Architecture

PhoneCam has four runtime parts.

1. Windows control app
   - Python + pywebview app in `phonecam/app`.
   - Detects Android devices with ADB.
   - Starts ADB reverse tunnels for local USB transport.
   - Receives Android frames and writes the shared frame buffer.

2. Android companion
   - Camera2 app in `android/phonecam-companion`.
   - Receives resolution, FPS, facing, and transport mode through ADB intent
     extras.
   - Captures camera frames and sends them to the Windows receiver.

3. Virtual camera package
   - UMDF stub driver registers `PhoneCam` as a Windows camera.
   - Media Foundation custom source serves frames to camera clients.
   - Current handoff is `%ProgramData%\PhoneCam\framebuffer.bin`.

4. Installer and release tooling
   - PowerShell scripts build native and Android artifacts.
   - WiX MSI packaging is the target for normal users.
   - Public releases require Microsoft driver signing.

Current production gap:

The working pipeline uses Android JPEG capture and Python/Pillow decode. This is
acceptable for a prototype, but the v1 performance target should move the hot
path to YUV or hardware video transport with native decode/write.

Current intent extras:

- `fps`: integer target FPS, default `30`.
- `resolution`: `WIDTHxHEIGHT`, default `1920x1080`.
- `facing`: `back` or `front`.
- `transport`: currently `jpeg`; reserved for `nv12`, `i420`, or hardware video
  modes.
