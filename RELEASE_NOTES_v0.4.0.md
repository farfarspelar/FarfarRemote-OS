# FarfarRemote 0.4.0 — draft release notes

FarfarRemote 0.4.0 provides two APKs from the same source tree.

## Choose an APK

- **FarfarRemote App** (`org.farfarremote.app`) is for everyday Android phones. It appears as a normal app and does not register as an Android HOME launcher. Android 4.4/API 19 or newer; no root or system changes.
- **FarfarRemote OS** (`org.farfarremote`) is for dedicated devices. It retains the HOME launcher behavior and package/signing update path for existing E2003 installations. Android 4.4/API 19 or newer. It is an Android launcher configuration, not a separate ROM.

Both are debug-signed APKs. Install the App APK as a separate app. For an existing OS installation, update only with the OS APK signed by its existing key; do not uninstall or clear app data.

## Changes

- Added Find My Kodi in the existing Kodi Connection Settings. It searches Kodi's HTTP JSON-RPC DNS-SD service on tap, checks selected endpoints over JSON-RPC, and only saves after explicit confirmation.
- Preserved manual host/port/username/password entry and current Settings design.
- Kept the Kodi client, preference keys and protected remote controls unchanged.
- Added normal App launcher integration while retaining OS HOME integration.

## Requirements

- Android 4.4 / API 19 or newer
- Kodi HTTP control enabled for JSON-RPC; Zeroconf announcements enabled for Find My Kodi
- App: `org.farfarremote.app`
- OS: `org.farfarremote`

Kodi can also be configured manually when discovery is unavailable. See [README](README.md) and [TEST_REPORT](TEST_REPORT.md).

## Checksums

See [SHA256SUMS-0.4.0.txt](dist/SHA256SUMS-0.4.0.txt).
