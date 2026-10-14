# FarfarRemote 0.4.7

Stable release. This release includes the swipe navigation and Kodi folder browser added during 0.4.6 development, along with the previously released Favorites, Kodi-host Power Off, and screen-timeout behavior.

## Choose the right APK

- **FarfarRemote App** — for everyday Android phones. Installs as a normal app and does not register as Android HOME. Android 4.4/API 19 or newer; target API 36. Package: `org.farfarremote.app`.
- **FarfarRemote OS** — for older or dedicated devices, including the Xperia E4g E2003. Can be selected as the Android HOME launcher. Android 4.4/API 19 or newer; target API 28. Package: `org.farfarremote`.

FarfarRemote OS is an Android launcher configuration, not a standalone ROM. Root, bootloader changes, and firmware flashing are not required.

## Downloads

- [FarfarRemote App APK](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.7/FarfarRemote-App-Android4.4plus-API19plus-v0.4.7.apk)
- [FarfarRemote OS APK](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.7/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.7.apk)
- [SHA-256 checksums](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.7/SHA256SUMS-0.4.7.txt)

## Changes

- Swipe left from the remote to open Settings; swipe right to open Kodi Library. Swipes inside Settings and Library navigate back; Kodi Library can move to its parent folder.
- Browse Kodi video folders and start selected media from the remote.
- Reopen the last successfully listed folder, and prefer the current playing item's parent folder when Kodi provides a usable path.
- Optionally remember audio and subtitle selections per folder using track metadata.
- Retain both App and OS distribution identities, launcher behavior, Kodi controls, Favorites, Find My Kodi, and manual connection settings.

## Install

Install the App APK for a normal phone. For an existing FarfarRemote OS installation, install only the OS APK as an update. Do not uninstall or clear app data. The APKs use the project's existing debug signing certificate; future in-place updates must keep the same certificate.

## Verification

Both variants built successfully and passed source-contract checks. Metadata and SHA-256 values were checked. The package minimum is API 19 for both; App targets API 36 and OS targets API 28. Physical swipe interaction on Samsung Android 13 and a new install/update on the Xperia were not performed as part of this release build.
