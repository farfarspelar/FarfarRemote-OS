# Changelog

## 0.4.9 — Media information, English descriptions, and OS idle polling

- Long file and episode titles in Kodi Library and the FarfarRemote playlist can now be swiped horizontally to read the full name; tapping the title still performs the row's existing action.
- Added a Kodi power menu with confirmed Sleep (Kodi `System.Suspend`) and Power Off actions. Power Off still sends the existing `System.Shutdown` request; sleep support depends on the Kodi host OS and hardware.
- Added an optional Now Playing information page to both App and OS flavors. Swipe horizontally over the Now Playing title area or use the information control in Kodi Library.
- Displays Kodi-provided artwork, plot, genres, year, media type, studio/director, rating, playback state, and active audio/subtitle tracks when available.
- Removed the Library Autoplay toggle and automatic folder-queue behavior; the manual playlist remains available.
- Replaced the Kodi-folder-scan opt-in with `Auto-scrape English descriptions`. It works for both App and OS, needs no provider account, API key, Kodi source setup, or scraper configuration, and is off by default.
- When enabled and Kodi has no synopsis, FarfarRemote automatically tries AniList for anime, English Wikipedia for film/TV summaries, and Wikidata for concise catalog descriptions. It matches titles conservatively, displays a source link, caches up to 40 results locally, and does not scan whole folders or libraries.
- IMDb remains a manual lookup link; automated IMDb scraping is excluded because IMDb prohibits website extraction and restricts its non-commercial datasets. TMDB is not bundled because it requires project-owned credentials and attribution.
- Retained Kodi as the first metadata source and the existing extended Kodi fields request. Playback and remote-control calls remain independent of optional online lookups.

- FarfarRemote OS now defaults to Balanced polling with a 10-second Kodi-idle interval on clean installs. Recent user input still triggers a prompt refresh, playback polling remains at 5 seconds, and screen-off suspends polling.
- Existing saved battery, connection, orientation, and display preferences are not overwritten. FarfarRemote App behavior is unchanged.
- Increased the versionCode to 17 so the update remains newer than the Xperia's preloaded system app across reboot.

## 0.4.8 — Library autoplay, playlists, and OS phone alert filter

- Raised the OS APK versionCode above the Xperia's preloaded system APK so Android keeps the update after reboot.
- Replaced the Kodi library's Settings shortcut with a persisted Autoplay toggle; Settings remains available through the existing swipe gesture.
- Added a local persistent playlist with add, reorder, remove, clear, and play controls. Autoplay builds a Kodi video queue from the selected file through the remaining files in the current folder, preserving Kodi's displayed order.
- Added an optional OS-flavor notification listener that can dismiss the stock Android no-SIM alert without disabling telephony packages or services. It requires the owner to grant Android Notification Access.

## 0.4.7 — Stable release

- Added swipe navigation from the remote to Kodi's video folders and Settings, with swipe-back behavior from both views.
- Added Kodi folder browsing, launching selected media, remembering the last successfully opened folder, and opening the folder of the currently playing item when Kodi provides that path.
- Added optional per-folder audio and subtitle preferences, matched using Kodi track metadata.
- Added OS-only Battery Mode profiles and bounded reconnect behavior while retaining immediate user commands and existing App behavior.
- Preserved both distribution identities, API 19 minimum, the OS HOME launcher, and the modern App target SDK.
- Includes the Favorites, Kodi Power Off, and screen-timeout behavior from 0.4.4.

## 0.4.6 RC5 — Open the folder currently playing

- When Kodi is playing media, opening the library first tries the parent directory of the active stream, so the browser returns to the folder the content came from instead of a generic source such as `Videos`.
- If Kodi cannot provide or list that stream directory, FarfarRemote falls back to the last successfully browsed location and then the existing source fallback.
- A failed stale-folder lookup no longer replaces the saved location with the fallback source.

## 0.4.6 RC4 — Remember Kodi browser location

- Restore the last successfully browsed Kodi folder when the library is reopened, including after leaving to the remote or restarting FarfarRemote.
- Save the location only after a folder/source listing succeeds. If the saved folder is no longer available, fall back to video sources without discarding the saved path.

## 0.4.6 RC3 — Kodi folder request and swipe-back fixes

- Simplified `Files.GetDirectory` requests to omit optional properties rejected by some Kodi JSON-RPC versions.
- Enabled contextual back swipes: right from Settings returns to the remote; left from Kodi Library returns to the remote; right in Kodi Library goes up one folder.
- Text-entry fields keep their normal horizontal editing gesture.

## 0.4.6 RC2 — Kodi folder browser navigation fix

- Reduced the horizontal swipe threshold so navigation is easier to trigger on smaller touchscreens.
- Added swipe-right navigation back to the parent Kodi folder; at the source/root view it returns to the remote.
- If Kodi cannot enumerate its reported current folder, the browser now falls back to configured video sources instead of stopping at an error.
- Added a Kodi JSON-RPC file-mode fallback for paths that cannot be listed in video mode.

## 0.4.6 RC1 — Swipe navigation and folder track preferences

- Added horizontal swipes on the remote screen: swipe left for Settings and swipe right for a Kodi folder browser.
- Added an in-app Kodi video source/folder browser using JSON-RPC; users can navigate folders and start a selected item without opening Kodi's TV-side menus.
- Added explicit per-folder audio and subtitle preference saving, matching tracks by language/name metadata instead of unstable stream indexes. Subtitle Off can be remembered; saved rules can be removed.
- Existing one-tap audio/subtitle selection and Kodi folder favorites remain available.

## 0.4.5 RC1 — OS battery optimization phase 1

- Added OS-only Normal, Balanced, and Maximum Battery Saving profiles with 2/5/10-second idle polling choices.
- Suspends OS status polling on screen-off and while Settings is open; resumes immediately on screen-on or when Settings closes.
- Adds bounded 2/4/8/16/30-second Kodi reconnect backoff and an optional 25% window-brightness override.
- Separates OS user-issued Kodi requests from background status polling so a poll cannot queue remote commands; the normal App executor remains unchanged.
- Added read-only, unplugged E2003 battery session and comparison tools. No endurance improvement is claimed without matched measurements.
- App flavor battery UI and polling policy remain unchanged. Existing Kodi settings and Keep Screen Awake preference are preserved.

## 0.4.4 RC1

- Added a Favorites button below the content shortcuts. Users can save the currently open Kodi folder locally, reopen it later, and remove saved paths.
- Clipped stray neighboring sprite fragments from the Home and Stop artwork without replacing the original PNG assets.
- Added a confirmed Power Off control that asks Kodi to shut down the Kodi host; the Android remote stays on.
- Bumped the App and OS distribution version to 0.4.4-rc1 while keeping their application IDs, API levels, and flavor-specific launcher behavior.

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
