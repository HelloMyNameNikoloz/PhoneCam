# Release Process

## Local Release

```powershell
powershell -ExecutionPolicy Bypass -File tools\release\create_local_release_package.ps1 -Version v1.0.0-beta.1
```

Output:

```text
release/v1.0.0-beta.1/
  PhoneCam-Setup-v1.0.0-beta.1.msi
  PhoneCam-Android-v1.0.0-beta.1.apk
  PhoneCam-v1.0.0-beta.1-checksums.txt
  PhoneCam-v1.0.0-beta.1-release-notes.md
```

## Publish On GitHub

1. Commit all changes.
2. Push main:

```powershell
git push origin main
```

3. Tag:

```powershell
git tag v1.0.0-beta.1
```

4. Push the tag:

```powershell
git push origin v1.0.0-beta.1
```

The GitHub Actions release workflow builds the Windows MSI, Android APK,
checksums, release notes, and GitHub Release automatically.

## Signing

Public v1 does not require EV certificate or Microsoft Hardware Dev Center
driver signing because it does not ship a custom camera driver package.

App/installer signing is optional for beta. Unsigned releases are allowed and
must publish SHA256 checksums. Future signing options can include SignPath
Foundation or another open-source-friendly code signing program.
