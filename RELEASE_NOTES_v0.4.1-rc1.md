# FarfarRemote 0.4.1 RC1

This is a release candidate for review and device testing. It is not a final stable release.

## Choose an APK

- **FarfarRemote App** (`org.farfarremote.app`) is the regular Android app for everyday phones. It appears in the app list and does not register as HOME.
- **FarfarRemote OS** (`org.farfarremote`) is for a dedicated Android device and retains HOME launcher behavior. It is an Android launcher configuration, not a separate Android ROM.

Both require Android 4.4 / API 19 or newer and share the Kodi controls and Settings. Kodi HTTP control is required; Find My Kodi also needs Kodi Zeroconf announcements and local multicast discovery.

## RC changes

The only application logic correction limits the existing Kodi state polling to the foreground activity lifecycle. This prevents periodic Kodi requests while the normal App edition is in the background and resumes polling when the app returns. Kodi command handling, discovery, Settings, saved preference keys, audio/subtitle selection, controls, and orientation implementation were not rewritten.

The App and OS variants are versioned `0.4.1-rc1` (versionCode 5). App ID remains `org.farfarremote.app`; OS ID remains `org.farfarremote`.

## Installation

Install the App APK as a normal Android app. It does not replace the system launcher.

For an existing FarfarRemote OS installation, install only the OS APK signed with the same certificate. Do not uninstall or clear data. The RC APKs are debug-signed with the local development key; these artifacts are suitable for this review/update path only if the signing certificate matches the existing installation. A production signing key must be selected and safely backed up before stable public updates.

## Validation scope

The Android API 19 build and package metadata were checked. The App RC was installed and launched on a Sony Xperia E4g E2003 running Android 4.4.4. Background polling was observed to stop after leaving the activity and resume after returning. See [TEST_REPORT.md](TEST_REPORT.md) for exact test boundaries.

No modern Android emulator was available. Kodi-connected controls and track selection were not re-exercised during the RC check; their implementation was left unchanged. HTTP JSON-RPC traffic is unencrypted and should be used on a trusted LAN.

## Artifacts and checksums

- `FarfarRemote-App-v0.4.1-rc1.apk` — regular Android app.
- `FarfarRemote-OS-v0.4.1-rc1.apk` — dedicated HOME launcher.
- SHA-256 sidecar files: `FarfarRemote-App-v0.4.1-rc1.apk.sha256` and `FarfarRemote-OS-v0.4.1-rc1.apk.sha256`; the combined manifest is `SHA256SUMS-0.4.1-rc1.txt`.
