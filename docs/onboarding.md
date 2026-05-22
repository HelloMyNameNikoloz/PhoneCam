# First-run onboarding

PhoneCam should guide non-technical users through setup inside the Windows app.

## Step 1: Camera device

Show whether the Windows camera device is installed:

- Installed and ready
- Installed but no frames
- Missing
- Repair required

If missing, show a single action: `Repair PhoneCam Camera`. The action should
request administrator privileges and explain why.

## Step 2: Connect Android

Show short instructions:

1. Connect the phone with USB.
2. Enable Developer Options.
3. Enable USB Debugging.
4. Accept the USB debugging prompt.

Unauthorized and offline states should be written in plain language with one
fix each.

## Step 3: Companion permission

PhoneCam installs and opens the Android companion through ADB. The Android app
requests only camera permission and then starts streaming automatically.

## Step 4: Preview

The Windows app shows the live preview and live performance metrics:

- Target FPS
- Capture FPS
- Bridge FPS
- Output FPS
- Dropped frames
- Latency
- Resolution

The preview can be disabled without stopping the virtual camera.

## Step 5: App test

Show: `PhoneCam is ready. Select PhoneCam in OBS, Zoom, Teams, Discord, or
browser camera settings.`

Offer quick checks:

- OBS Video Capture Device
- Browser camera test
- Windows Camera app

## Step 6: Troubleshooting

Use targeted messages instead of walls of text:

- Camera device missing: repair driver installation.
- Driver installed but no frames: check Android permission and USB tunnel.
- Unauthorized: unlock phone and accept RSA prompt.
- Offline: reconnect USB or change USB mode.
- Low FPS: use 1080p30, close background apps, lower resolution.
- Black output: restart client app or run repair.
