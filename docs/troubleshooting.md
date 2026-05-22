# Troubleshooting

## PhoneCam Does Not Appear

1. Confirm you are on Windows 11.
2. Open PhoneCam.
3. Go to Setup.
4. Click Repair PhoneCam Camera.
5. Restart the target app and select `PhoneCam`.

If the app says the driverless camera API is unavailable, public v1 is not
supported on that Windows build.

## Phone Is Unauthorized

Unlock the phone and accept the USB debugging prompt. If the prompt does not
appear, revoke USB debugging authorizations in Android Developer Options and
connect again.

## Phone Is Offline

Reconnect the cable or switch USB mode to Charging only, PTP, or file transfer.
Avoid USB hubs for first setup.

## Black Camera Output

Open PhoneCam and check:

- Android permission state.
- Capture/Bridge FPS.
- Virtual camera status.
- Whether the Android companion shows streaming.

Use Setup > Repair PhoneCam Camera if `PhoneCam` appears but clients receive no
frames.

## Low FPS

Use 1080p30 first. If actual FPS is below target, reduce resolution, close other
camera apps, use a direct USB cable, and keep Live Preview off while testing.

## SmartScreen Warning

Unsigned public beta builds may show Windows SmartScreen warnings. Verify the
SHA256 checksums published with the GitHub Release.
