# Windows Support

## Public V1

PhoneCam public v1 targets Windows 11.

The public v1 camera registration path uses the Media Foundation driverless
virtual camera API. This avoids custom driver packages, EV certificate
requirements, Hardware Dev Center signing, and Windows Test Mode.

## Windows 10

Windows 10 support is experimental. If the driverless virtual camera API is not
available, PhoneCam should show an unsupported message instead of falling back to
test-signed driver instructions.

The legacy driver path can be used by contributors for research, but it is not a
public v1 install path.

## Secure Boot

Secure Boot can stay enabled for public v1 because the normal installer does not
load a custom kernel or UMDF camera driver package.
