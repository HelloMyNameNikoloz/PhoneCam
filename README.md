# PhoneCam

PhoneCam is now rooted at this directory.

- `phonecam/` contains the Python desktop control app.
- `native/phonecam_virtual_camera/` contains the v2 Windows virtual camera package.
- `native/vendor/` contains Microsoft sample code used as the base for the Frame Server camera implementation.
- `tools/` contains build and install helpers.

## V2 Direction

The real camera device path is Windows Frame Server Custom Media Source:

1. A UMDF stub driver registers `PhoneCam` under the Windows camera categories.
2. A COM media source DLL provides frames to Windows camera clients.
3. The Python app remains the control surface for Android detection and capture settings.

Building and installing the native camera requires Visual Studio Build Tools plus the Windows Driver Kit.
