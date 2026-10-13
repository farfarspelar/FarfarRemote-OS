# Changelog

## 0.4.1 RC1 — 2026-10-13

- Added lifecycle handling so Kodi status polling runs only while the remote activity is in the foreground, then resumes when the user returns.
- Prepared separate App and OS release-candidate APKs with versionCode 5 while preserving their application IDs and shared codebase.
- Updated public documentation and release verification records.
- No Kodi command, discovery, Settings, audio/subtitle, orientation, or launcher behavior was intentionally redesigned.

## 0.4.0 — 2026-10-13

- Added `app` and `os` Gradle product flavors sharing Kodi and UI code.
- App (`org.farfarremote.app`) has a normal launcher icon and no HOME intent; OS retains `org.farfarremote` and HOME behavior for in-place dedicated-device updates.
- Added on-demand Find My Kodi discovery using Kodi HTTP JSON-RPC DNS-SD, endpoint verification, explicit save confirmation, timeout, and lifecycle cleanup.
- Preserved manual Kodi configuration, existing preference keys, and core Kodi client behavior.
- Added separate App/OS build and install scripts.

## 0.3.0

- Redesigned Settings using themed cards, scrollable fields, input focus graphics, and stateful orientation and remote controls.
- Preserved existing Kodi preference keys, application identity, HOME launcher, Kodi client, remote actions, D-pad, Audio/Subtitles, and orientation policy.
- Added the optional Buy Me a Coffee external link with clipboard fallback when no browser is available.
- Integrated selected user-provided Settings assets and documented their provenance and licensing status.

## 0.2.0

- Added portrait-first remote layouts with dedicated portrait and landscape designs and persisted Portrait/Landscape/Auto selection.
- Added transparent remote controls, bounded artwork decoding, Kodi artwork loading, and a neutral missing-art placeholder.
- Added Settings for Kodi connection and display/remote preferences while preserving 0.1 preference keys.
- Added Kodi JSON-RPC playback, metadata, seek, audio/subtitle selection, navigation, media windows, and volume controls.
- Added an app-ready splash overlay. Android boot animation, system partitions, root, and debloat were not changed.
