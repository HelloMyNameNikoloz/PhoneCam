# Security Policy

PhoneCam handles live camera frames. Treat regressions that expose frames,
enable remote access, or install untrusted camera components as security issues.

## Supported Versions

Only tagged beta and stable releases are supported. Development builds are best
effort.

## Reporting a Vulnerability

Open a private security advisory on GitHub when the repository is public. Until
then, contact the maintainers privately and include:

- PhoneCam version or commit.
- Windows version and Android version.
- Whether the driverless camera registration succeeds in PhoneCam Setup.
- Exact steps to reproduce.
- Logs with camera frames and personal identifiers removed.

## Privacy and Local Transport Rules

- PhoneCam must not send frames to cloud services.
- Local frame receivers must bind to `127.0.0.1` only.
- USB mode uses ADB reverse so the Android app connects to localhost on the
  phone and reaches localhost on the PC through USB.
- Logs must never include frame bytes, screenshots, or saved camera images.
- Runtime frame buffers under `%ProgramData%\PhoneCam` must be cleared or
  overwritten with a black frame when the app exits.
- Telemetry is off by default. Do not add network telemetry without explicit
  opt-in and documentation.
