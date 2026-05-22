# Privacy

PhoneCam is designed as a local USB camera bridge.

- No cloud service is required.
- No account is required.
- No telemetry is collected by default.
- Camera frames are transported over USB through ADB reverse to `127.0.0.1`.
- The Windows app writes the latest frame to `%ProgramData%\PhoneCam` so the
  local virtual camera source can serve it to apps such as OBS, Zoom, Teams,
  Discord, browsers, and Windows Camera.
- PhoneCam does not intentionally save recordings, screenshots, or frame history.

Runtime files:

- `%ProgramData%\PhoneCam\framebuffer.bin` contains the latest live frame while
  the camera is active.
- `%ProgramData%\PhoneCam\native_stats.bin` contains frame counters and timing.
- `%ProgramData%\PhoneCam\native_settings.txt` contains selected resolution/FPS.
- `%APPDATA%\PhoneCam\settings.json` contains user settings.

The app should clear or black out the frame buffer on stop/exit. The installer
removes runtime files during uninstall. Diagnostic exports must not include frame
payloads, usernames, or full device serials unless the user explicitly chooses to
share them.
