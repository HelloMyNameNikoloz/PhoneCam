# PhoneCam Desktop App

This folder contains the Python + pywebview control app for PhoneCam.

Run from source:

```powershell
python -m pip install -r requirements.txt
python app/main.py
```

Build the local EXE:

```powershell
python build_tools\build_exe.py
```

The EXE is a build artifact and is intentionally ignored by git.

Runtime responsibilities:

- expose the pywebview bridge to the UI
- detect Android devices with bundled ADB
- set up ADB reverse USB tunnels
- install/start the Android companion APK when available
- receive Android frames on localhost
- write frames and settings under `%ProgramData%\PhoneCam`
- show preview, status, logs, and performance diagnostics

The current hot path uses JPEG frames and Pillow decode. This is a temporary
implementation. See `../docs/performance-roadmap.md` for the native/YUV pipeline
planned before stable release.
