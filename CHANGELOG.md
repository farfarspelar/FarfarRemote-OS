# Changelog

## 0.2.0

- Reworked the existing `org.farfarremote` app into portrait-first full-screen portrait and landscape remote layouts, with persisted Portrait/Landscape/Auto selection.
- Integrated individually cropped transparent controls, bounded artwork decoding, Kodi artwork loading and a neutral no-art placeholder. Original asset files remain separate.
- Added Settings for Kodi address and credentials, connection test, display mode, screen-awake, reconnect and haptics; retained 0.1 preference keys.
- Added a Kodi JSON-RPC client for connection/player state, metadata, seek/progress, audio/subtitle selection, playback, navigation, media windows and volume/mute.
- Added an app-ready splash overlay. Android boot animation, system partitions, root and debloat were not changed.
- Updated package version from 0.1.0 to 0.2.0; minSdk remains 19. No new third-party libraries or Play Services.
