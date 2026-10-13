# Changelog

## 0.3.0

- Redesigned Settings in the existing activity with four themed cards, scrollable fields, focus-state input graphics and stateful orientation/remote switches.
- Kept existing Kodi preference keys, Android application ID, HOME launcher, Kodi client, remote action methods, D-pad, Audio/Subtitles and orientation policy.
- Added a discreet optional Buy Me a Coffee link to the owner-provided URL. It uses `ACTION_VIEW`; when no handler exists, the link is copied to the clipboard.
- Integrated selected user-supplied Settings PNGs, retaining the extracted original pack and scaling 128 px icons to 64 px.
- Added a Settings contract test and updated documentation. VersionCode is 3; minSdk remains 19; no new library dependencies.

## 0.2.0

- Reworked the existing `org.farfarremote` app into portrait-first full-screen portrait and landscape remote layouts, with persisted Portrait/Landscape/Auto selection.
- Integrated individually cropped transparent controls, bounded artwork decoding, Kodi artwork loading and a neutral no-art placeholder. Original asset files remain separate.
- Added Settings for Kodi address and credentials, connection test, display mode, screen-awake, reconnect and haptics; retained 0.1 preference keys.
- Added a Kodi JSON-RPC client for connection/player state, metadata, seek/progress, audio/subtitle selection, playback, navigation, media windows and volume/mute.
- Added an app-ready splash overlay. Android boot animation, system partitions, root and debloat were not changed.
- Updated package version from 0.1.0 to 0.2.0; minSdk remains 19. No new third-party libraries or Play Services.
# 0.4.0 — 2026-10-13

- Added `app` and `os` Gradle product flavors sharing all Kodi and UI code.
- App flavor (`org.farfarremote.app`) has a normal launcher icon and no HOME intent; OS flavor retains `org.farfarremote` and HOME launcher behavior for in-place Xperia updates.
- Added tap-to-search Find My Kodi via Kodi HTTP JSON-RPC DNS-SD, with endpoint verification, explicit save confirmation, timeout and lifecycle cleanup.
- Kept manual Kodi configuration, preference keys and core Kodi client unchanged.
- Added separate App/OS build and install scripts plus versioned APK/checksum artifacts.
