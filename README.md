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

Building the native camera requires Visual Studio Build Tools 2022, Windows SDK 10.0.26100, and WDK 10.0.26100.

```powershell
.\tools\build_native_camera.ps1
```

Installing/registering the camera requires an elevated PowerShell session:

```powershell
.\tools\install_virtual_camera.ps1
```

Current v2 status:

- The native package builds and produces a signed catalog.
- The INF registers the Windows camera device as `PhoneCam`.
- The media source still uses the sample frame generator until the Android frame bridge is wired in.
