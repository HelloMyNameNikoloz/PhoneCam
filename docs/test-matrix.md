# Beta test matrix

Use this matrix before every public beta.

## Windows

| Area | Windows 10 | Windows 11 |
| --- | --- | --- |
| Clean install with Secure Boot enabled | Experimental | Pending |
| Repair install restores PhoneCam camera | Pending | Pending |
| Uninstall removes app and camera device | Pending | Pending |
| Non-admin launch has clear unsupported/repair guidance | Pending | Pending |

## Camera clients

| Client | 720p30 | 1080p30 | 1080p60 | Notes |
| --- | --- | --- | --- | --- |
| OBS Studio Video Capture Device | Pending | Required | Optional | Device Default and Custom |
| Chrome getUserMedia | Pending | Required | Optional | Camera permission dropdown |
| Edge getUserMedia | Pending | Required | Optional | Camera permission dropdown |
| Firefox getUserMedia | Pending | Required | Optional | Camera permission dropdown |
| Discord | Pending | Required | Optional | Camera settings preview |
| Zoom | Pending | Required | Optional | Meeting preview |
| Microsoft Teams | Pending | Required | Optional | Device settings preview |
| Windows Camera | Pending | Best effort | Optional | Depends on OS camera stack |

## Stability

| Scenario | Target |
| --- | --- |
| 1080p30 OBS soak | 30 minutes, no crash, no black frames |
| Phone unplug/replug | 10 cycles, automatic recovery |
| Android companion restart | Automatic recovery |
| OBS deactivate/reactivate | Camera remains selectable and live |
| Windows sleep/wake | Clear recovery or clear error |
| OBS plus browser preview | No source deadlock |

## Privacy/security

| Check | Target |
| --- | --- |
| Local listeners | Bind only to 127.0.0.1 |
| Logs | No frame payloads, no unnecessary identifiers |
| Stop/exit | Frame buffer blacked or cleared |
| Android permissions | Camera only |
| Telemetry | Off by default; none in v1 |
