# FarfarRemote 0.4.2 RC1 — split Android release tracks

This is a release candidate. It is not a stable/public release.

## Editions

- **FarfarRemote App** (`org.farfarremote.app`) is the regular app for everyday phones. It does not claim Android HOME. It has minSdk 19 and targetSdk 36.
- **FarfarRemote OS** (`org.farfarremote`) is the Android HOME launcher for old or dedicated devices, including the tested Xperia E4g E2003. It retains minSdk 19 and targetSdk 28.

Both APKs are built from the same source and share Kodi behavior, UI, Settings, discovery, and preferences. Only App-specific modern system behavior is enabled in its flavor. FarfarRemote OS remains an Android launcher application, not a custom ROM.

## Changes

- Raised only the App flavor target to API 36 to adopt current Android target behavior. API 36 is also the current Google Play target for new apps and updates as of August 31, 2026.
- Kept both minimum SDKs at API 19. APIs introduced after API 19 are isolated behind runtime checks; the App remains installable on older devices, although its modern UI behavior is intended for newer phones.
- Added App-only system bar/cutout/keyboard inset handling for Android 15+ edge-to-edge, and a platform Back callback to close Settings on Android 13+.
- Kept OS targetSdk 28, package ID `org.farfarremote`, HOME intent, and stored preference keys unchanged.
- Documented the owner-reported ChatGPT graphics generation process and checked for official third-party logos; none are bundled.

## Requirements and Kodi connectivity

- App: Android 4.4/API 19 or newer; target API 36.
- OS: Android 4.4/API 19 or newer; target API 28.
- Kodi HTTP control / JSON-RPC is required. Find My Kodi additionally requires Kodi Zeroconf announcements and local multicast.
- Kodi HTTP is unencrypted. Use a trusted LAN. The explicit cleartext allowance remains necessary for ordinary Kodi HTTP endpoints.
- Apps targeting API 37 will need a local-network permission or a system-mediated service picker. This release targets API 36 and does not request that API 37 permission.

## Install

Download [FarfarRemote-App-Android4.4plus-API19plus-v0.4.2-rc1.apk](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.2-rc1/FarfarRemote-App-Android4.4plus-API19plus-v0.4.2-rc1.apk) for an everyday phone. It opens from the app drawer and does not replace the phone launcher. Minimum: Android 4.4/API 19; target API 36. Android 13 device use was reported by the project owner; Android 13 and 15 emulator smoke checks passed.

Download [FarfarRemote-OS-Android4.4plus-API19plus-v0.4.2-rc1.apk](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.2-rc1/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.2-rc1.apk) for a dedicated device, including the Xperia E4g E2003. Minimum: Android 4.4/API 19; target API 28. For an existing OS install, update in place with the OS APK only, signed with the same certificate; do not uninstall or clear data.

These RC APKs are debug-signed. They are for testing, not a finalized production signing policy. See [README](README.md) and [TEST_REPORT](TEST_REPORT.md).

Verify downloads with [SHA256SUMS-0.4.2-rc1.txt](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.2-rc1/SHA256SUMS-0.4.2-rc1.txt). The APK filenames include the minimum Android version and API level.

## Verification status

The API 36/App and API 28/OS variants compile and package metadata is checked. The OS update path is tested on the physical E2003. The API 36 App has not yet been tested on Android 13 Samsung hardware or Android 15/16 hardware in this environment. Do not interpret build success as full device QA.

## Graphics provenance

The UI artwork and visual references are documented as generated with ChatGPT from prompts written and directed by the project owner. No official Kodi or Buy Me a Coffee logos are bundled. See [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md).
