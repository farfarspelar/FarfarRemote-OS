# Changelog

## Unreleased

- Added a confirmed Power Off control that asks Kodi to shut down the Kodi host; the Android remote stays on.

## 0.4.3 RC1 — Screen timeout default

- FarfarRemote no longer keeps the display awake by default. Android's configured screen timeout is now honored; the Xperia E2003's current timeout is 30 seconds.
- Kept the existing **Keep Screen Awake** override and preference key for users who choose to prevent the screen from sleeping.
- Built separate App and OS APKs with updated version metadata; package IDs, launcher behavior, minimum API, and Kodi implementation are unchanged.

## 0.4.2 RC1 — Release track SDK split

- Split the target SDK strategy: FarfarRemote App targets API 36; FarfarRemote OS stays at API 28 for the proven Xperia HOME setup.
- Both tracks retain minSdk API 19, shared Kodi/features, and their established distinct application IDs.
- Added App-only edge-to-edge insets for status/navigation bars, cutouts, and the keyboard, plus the platform Back callback for Settings on Android 13+.
- Documented the owner-reported ChatGPT graphics provenance and the distinction between project art and third-party names.
- Modern Android runtime behavior still needs device verification; see `TEST_REPORT.md`.

## 0.4.1 RC1 — 2026-10-13

- Limited the existing Kodi state polling to the foreground Activity lifecycle to avoid polling while the normal App was in the background.
- Preserved the App and OS application IDs, HOME intent in OS only, and all Kodi, discovery, Settings, audio/subtitle, and orientation implementations.

## 0.4.0 — 2026-10-13

- Added `app` and `os` Gradle flavors sharing Kodi and UI code.
- App (`org.farfarremote.app`) has a normal launcher icon and no HOME intent; OS retains `org.farfarremote` and HOME behavior for in-place dedicated-device updates.
- Added on-demand Find My Kodi discovery using Kodi HTTP JSON-RPC DNS-SD, endpoint verification, explicit save confirmation, timeout, and lifecycle cleanup.
- Preserved manual Kodi configuration, existing preference keys, and core Kodi client behavior.

## 0.3.0

- Redesigned Settings using themed cards, scrollable fields, input focus graphics, and stateful orientation and remote controls.
- Preserved existing Kodi preference keys, application identity, HOME launcher, Kodi client, remote actions, D-pad, Audio/Subtitles, and orientation policy.
- Added the optional Buy Me a Coffee external link with clipboard fallback when no browser is available.
- Integrated generated Settings assets and documented their provenance.

## 0.2.0

- Added portrait-first remote layouts with dedicated portrait and landscape designs and persisted Portrait/Landscape/Auto selection.
- Added transparent remote controls, bounded artwork decoding, Kodi artwork loading, and a neutral missing-art placeholder.
- Added Settings for Kodi connection and display/remote preferences while preserving 0.1 preference keys.
- Added Kodi JSON-RPC playback, metadata, seek, audio/subtitle selection, navigation, media windows, and volume controls.
- Added an app-ready splash overlay. Android boot animation, system partitions, root, and debloat were not changed.
