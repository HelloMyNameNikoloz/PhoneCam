# PhoneCam OBS Source

PhoneCam v2 can feed OBS without opening a separate preview window.

## How it works

- Windows PhoneCam hosts a local receiver on port `4767`.
- Android PhoneCam Sender posts camera frames to `http://PC-IP:4767/frame`.
- OBS reads the live feed from `http://127.0.0.1:4767/obs` as a Browser Source.

## OBS setup

1. Open the Windows PhoneCam app.
2. Add a Browser Source in OBS.
3. Set the URL to `http://127.0.0.1:4767/obs`.
4. Set width and height to the selected capture size, usually `1920` by `1080`.
5. Keep audio as a separate microphone source.

## Android setup

1. Build and install the sender:

   ```powershell
   .\tools\build_android_sender.ps1 -Install
   ```

2. Copy the Android sender URL from the Windows app.
3. Paste it into PhoneCam Sender on Android.
4. Tap Start stream.

The Android app auto-starts on future launches when a receiver URL is saved.

## Device dropdown limitation

OBS `Video Capture Device > Device > PhoneCam` requires a signed Windows camera driver or Frame Server media source. The OBS Browser Source path avoids that native signing requirement but is not the same as a system camera device.
