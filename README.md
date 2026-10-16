# FarfarRemote

A lightweight Kodi remote for Android, available as a regular app or a dedicated remote-control launcher.

## Choose your edition

### FarfarRemote App — modern mobile track

For everyday Android phones. It installs as a regular app, appears in the app drawer, and never registers as Android HOME. It is the recommended choice for phones used day to day.

- Minimum Android version: Android 4.4 / API 19.
- Target Android version: Android 16 / API 36.
- Newer Android APIs are guarded at runtime so the package can retain its broad install range.

### FarfarRemote OS — legacy dedicated-device track

For old or dedicated Android devices, especially repurposed hardware such as the Sony Xperia E4g E2003. It can be selected as the Android HOME launcher and retains the compatibility settings used by the tested Xperia installation.

- Minimum Android version: Android 4.4 / API 19.
- Target Android version: Android 9 / API 28, intentionally conservative for the legacy HOME-device setup.
- FarfarRemote OS is still an Android application and launcher configuration, not a separate Android ROM. Root, firmware modification, and debloating are not required.

Both editions share the Kodi client, controls, Settings, graphics, and Find My Kodi. They have different application IDs and can be installed side by side:

| Edition | Application ID | Android SDK strategy |
| --- | --- | --- |
| FarfarRemote App | `org.farfarremote.app` | min API 19, target API 36 |
| FarfarRemote OS | `org.farfarremote` | min API 19, target API 28 |

## Screenshots

The screenshots show the App edition on a Sony Xperia E4g E2003 (Android 4.4/API 19), offline. No Kodi connection or media is shown.

**Portrait remote**

![FarfarRemote portrait remote](docs/screenshots/farfarremote-app-portrait.png)

**Landscape remote**

![FarfarRemote landscape remote](docs/screenshots/farfarremote-app-landscape.png)

**Settings**

![FarfarRemote Settings](docs/screenshots/farfarremote-app-settings.png)

## Features

- D-pad and OK, Back, Kodi Home, play/pause, stop, previous/next, rewind/fast-forward, volume and mute.
- Kodi power menu with confirmed Sleep (Suspend) and Power Off actions. Sleep support depends on the Kodi host; neither action powers off the Android remote.
- Kodi Now Playing information, artwork, playback progress, and seek controls.
- Experimental media information page with Kodi-provided metadata when available and an opt-in automatic English description lookup for movies and anime. When enabled, FarfarRemote tries AniList for anime, then English Wikipedia and Wikidata as broad fallbacks, and shows the source and a link to it. Results are cached locally for up to 40 titles.
- Automatic lookup is off by default. Turn on `Auto-scrape English descriptions` in Settings; no provider account, API key, Kodi video-source setup, or scraper configuration is needed. While enabled, media titles are sent to AniList, English Wikipedia, and/or Wikidata only when Kodi has no plot. The app looks up the currently playing item, not entire folders or libraries.
- IMDb remains available as a manual title link. FarfarRemote does not scrape IMDb: IMDb prohibits automated website extraction and restricts use of its downloadable datasets. TMDB is not included because it requires a project-owned API credential and attribution; credentials must not be embedded in a public APK.
- Online summaries are best-effort. Exact title matching is used to reduce false matches; obscure, renamed, or poorly catalogued files may have no result. Kodi metadata remains the preferred source.
- Audio and subtitle stream selection on the remote, including subtitle Off when Kodi provides it.
- Swipe left on the remote screen to open Settings; swipe right to browse Kodi video sources and folders, then start a selected item from the phone.
- Audio or subtitle choices can be remembered explicitly per media folder using Kodi's reported language/name metadata. Rules can be forgotten and do not rely on stream indexes.
- Local folder favorites: save the currently open Kodi folder with a chosen name and reopen it from the Favorites button beneath the Movies/TV Shows/Music/Add-ons shortcuts.
- Portrait, landscape, and automatic orientation modes.
- Saved Kodi connection settings, optional keep-awake, reconnect, and haptic settings.
- Find My Kodi searches for Kodi's DNS-SD/Zeroconf HTTP JSON-RPC service only when requested. It verifies a selected endpoint and asks before saving it. Discovery does not run in the background.
- Manual host, port, username, and password entry remains available when discovery is unavailable.
- Optional external support link: <https://buymeacoffee.com/farfarspelar>.

The Kodi power control offers **Sleep (Suspend)** and **Power Off**, each with a confirmation step. Sleep sends Kodi's `System.Suspend` request and depends on the operating system, hardware, and power configuration of the Kodi device. Power Off continues to send `System.Shutdown`. See Kodi's [JSON-RPC system methods](https://kodi.wiki/view/JSON-RPC_API/v13.11#System).

The owner reports that all current features have been tested and work in both the App and OS editions. The OS edition and active-stream folder browser have been physically checked on the Xperia E2003; the owner has also reported FarfarRemote App running on a Samsung Android 13 phone. These are owner-reported device checks, separate from automated source-contract checks.

## Android compatibility and security notes

The App track targets API 36 to adopt modern Android behavior and meet the current Google Play target API requirement. Android 15 and later enforce edge-to-edge for apps targeting API 35+, so the App applies system bar, display cutout, and keyboard insets. On Android 13+, App Settings uses the platform Back callback. The OS track remains target API 28 to protect the established Xperia behavior. See Android's [target API requirements](https://developer.android.com/google/play/requirements/target-sdk), [Android 15 behavior changes](https://developer.android.com/about/versions/15/behavior-changes-15), and [Android 16 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-16).

Android 17 / API 37 requires local network permission or a system-mediated picker for apps that access LAN devices. This project currently targets API 36, so it does not request that permission yet. Before a target 37 update, Find My Kodi and direct Kodi connections must be migrated and tested under the new policy. See [local network permission guidance](https://developer.android.com/privacy-and-security/local-network-permission).

Kodi's built-in JSON-RPC connection uses HTTP. FarfarRemote must allow cleartext traffic for Kodi communication and currently uses it for configured connections; HTTP does not encrypt Kodi credentials or commands. Use a trusted local network. The target SDK improves platform behavior but cannot make Kodi's HTTP protocol encrypted.

## Kodi setup and connection

Enable Kodi's web server / HTTP control, then enter the Kodi hostname or IP, port, and any credentials in FarfarRemote Settings. The default port shown by Kodi is commonly 8080, but use the port configured in your Kodi installation.

Find My Kodi additionally needs Kodi Zeroconf service announcements and multicast discovery on the local network. Guest Wi-Fi, client isolation, multicast filtering, and firewalls may prevent discovery. If no device is found, use the visible manual connection fields. A discovered endpoint is tested with JSON-RPC and is not saved until you confirm it.

## Download and install

### Latest stable release: v0.4.7

- **FarfarRemote App — Android 4.4+ (API 19+)** — [Download the regular Android app](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.7/FarfarRemote-App-Android4.4plus-API19plus-v0.4.7.apk). For everyday phones, including Android 13 and Android 15. It does not register as the HOME launcher. Target API 36.
- **FarfarRemote OS — Android 4.4+ (API 19+)** — [Download the dedicated-device launcher](https://github.com/farfarspelar/FarfarRemote-OS/releases/download/v0.4.7/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.7.apk). For older or dedicated devices such as the Xperia E4g E2003. Target API 28 and includes the HOME launcher intent.

See the [v0.4.7 release notes and SHA-256 checksums](https://github.com/farfarspelar/FarfarRemote-OS/releases/tag/v0.4.7) or browse [all GitHub Releases](https://github.com/farfarspelar/FarfarRemote-OS/releases). Install the App APK as a normal app and open it from the app drawer. For an existing FarfarRemote OS installation, update with the OS APK only; do not uninstall the app or clear its data. Android may ask you to allow APK installation from your browser or file manager.

### Development build — `feature/now-playing-info-page`

These branch builds include the experimental metadata page and opt-in English descriptions, Kodi Sleep/Suspend, and horizontal title scrolling in Library and Playlist. They are signed with the existing project debug certificate and have not completed full physical-device regression testing.

- [FarfarRemote App v0.4.9 development APK](dist/FarfarRemote-App-Android4.4plus-API19plus-v0.4.9-dev.apk) — regular app, no HOME launcher role.
- [FarfarRemote OS v0.4.9 development APK](dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.9-dev.apk) — dedicated HOME launcher for Android devices.
- [Development APK SHA-256 checksums](dist/SHA256SUMS-0.4.9-dev.txt).

## Build from source

Requirements: JDK 17 or newer, Android SDK Platform 36, Android SDK Build Tools 35.0.0, Python 3, and the included Gradle wrapper. Set `ANDROID_HOME` or `ANDROID_SDK_ROOT` to the SDK path.

```sh
python3 tools/test_v03_contract.py
./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug
./tools/build_distributions.sh
```

Gradle flavors are named `app` and `os`. Both APKs compile against API 36 and require Android 4.4 / API 19 or newer. The App flavor targets API 36 and the OS flavor targets API 28. The script builds, checks package IDs and SDK metadata, and writes the clearly labeled APKs and SHA-256 files under `dist/`.

## Signing and updates

The v0.4.7 APKs are signed with the project's existing Android debug certificate so they can update compatible installations using the established signing identity. This certificate is suitable for this project's direct-download distribution but is not a private production signing key. Android permits an in-place update only when both the application ID and signing certificate match. Do not uninstall an existing `org.farfarremote` installation or clear its data to work around a signature mismatch.

## Graphics provenance

The project owner reports that FarfarRemote's UI graphics and visual references were generated with ChatGPT from prompts written by the owner, who directed the visual design. The generated images were integrated as FarfarRemote UI assets and references. App code and Android XML drawables are project-authored source code under GPL-3.0. No official Kodi or Buy Me a Coffee logo is included; the coffee cup is a generic generated project graphic. See [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md) for the inventory and notes.

## Known limitations

- The legacy OS track is primarily verified on a Sony Xperia E4g E2003 running Android 4.4/API 19.
- The user reports FarfarRemote App runs without problems on a Samsung phone with Android 13. API 33 and API 35 emulator smoke checks also passed for the App track; those checks do not replace testing across other device makers and models.
- Kodi discovery depends on Zeroconf announcements and multicast support; manual connection is the fallback.
- Kodi HTTP JSON-RPC is unencrypted.
- Kodi determines which artwork and media metadata are available.
- The OS edition is not a ROM and performs no root, firmware, bootloader, or system-package modification.

## License and support

FarfarRemote application code is licensed under [GPL-3.0](LICENSE). Generated graphics are documented separately in [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md) and [graphics/README.md](graphics/README.md).

Optional support: <https://buymeacoffee.com/farfarspelar>.
