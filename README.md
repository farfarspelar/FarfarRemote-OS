# FarfarRemote

A lightweight Kodi remote for Android, available as a regular app or a dedicated remote-control launcher.

## Choose your edition

### FarfarRemote App

For everyday Android phones. Install the APK and use it like any other app. It requires no root or system modification, does not register as the HOME launcher, and is the recommended edition for most users. Android's normal launcher and Home button remain in control.

### FarfarRemote OS

For old or dedicated Android devices. This edition can be selected as the Android HOME launcher and opens directly into FarfarRemote's dedicated remote interface. It still runs on Android; it is not a separate ROM. Optional Android debloating or system optimization is a separate advanced procedure and is not required.

Both editions share the same Kodi controls, discovery, Settings, and graphics. They have different application IDs and can be installed side by side:

| Edition | Application ID | Intended use |
| --- | --- | --- |
| FarfarRemote App | `org.farfarremote.app` | Normal Android app |
| FarfarRemote OS | `org.farfarremote` | Dedicated HOME launcher |

## Screenshots

These screenshots show the App edition running on a Sony Xperia E4g E2003 (Android 4.4/API 19). The app was offline during capture; no Kodi connection or media is shown.

**Portrait remote**

![FarfarRemote portrait remote](docs/screenshots/farfarremote-app-portrait.png)

**Landscape remote**

![FarfarRemote landscape remote](docs/screenshots/farfarremote-app-landscape.png)

**Settings**

![FarfarRemote Settings](docs/screenshots/farfarremote-app-settings.png)

## Features

- D-pad with OK, Back, Home, playback and transport controls, volume and mute.
- Kodi Now Playing details, artwork, playback progress and seek controls.
- Audio and subtitle stream selection on the remote, including subtitle Off where Kodi provides it.
- Portrait, landscape and automatic orientation modes.
- Saved Kodi connection settings and optional screen-awake, reconnect and haptic settings.
- Find My Kodi searches for Kodi's DNS-SD/Zeroconf HTTP JSON-RPC service when requested. It verifies a selected endpoint and asks before saving it. Discovery is not a background scan.
- Manual host, port, username and password entry remains available when discovery is unavailable.
- Optional Buy Me a Coffee link: <https://buymeacoffee.com/farfarspelar>.

## Requirements and Kodi setup

- Android 4.4 / API 19 or newer. The project currently targets Android 9 / API 28.
- Kodi must be reachable over the local network. Enable Kodi's web server / HTTP control and configure its port and credentials in FarfarRemote Settings.
- Find My Kodi additionally requires Kodi Zeroconf announcements and multicast discovery to be available on the local network. Network isolation, guest Wi-Fi, access point multicast filtering, or firewalls can prevent discovery; enter the address manually in that case.
- FarfarRemote uses Kodi's HTTP JSON-RPC endpoint. Use it on a trusted local network; HTTP does not encrypt credentials or control traffic.

## Download and install

Download APKs from the [GitHub Releases page](https://github.com/farfarspelar/FarfarRemote-OS/releases). Choose the edition that matches your use:

- **App:** install `FarfarRemote-App-<version>.apk`, then open FarfarRemote from the normal app list. It does not take over HOME.
- **OS:** install `FarfarRemote-OS-<version>.apk` on a dedicated device. To make it the default launcher, press Android Home and select FarfarRemote. For an existing OS installation, install an update with the OS APK only; do not uninstall the app or clear its data. Keep using APKs signed with the same key as the installed OS version.

Android may require the user to allow installation from the chosen file manager or browser. The release APKs are currently debug-signed development builds; see [Signing and updates](#signing-and-updates).

## Build from source

Requirements: JDK, Android SDK Platform 34 and Build Tools 34.0.0, Python 3, and the included Gradle wrapper. Set `ANDROID_HOME` or `ANDROID_SDK_ROOT` to the SDK path. Then run:

```sh
python3 tools/test_v03_contract.py
./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug
./tools/build_distributions.sh
```

The distribution script writes the App APK, OS APK and SHA-256 manifest under `dist/`. The flavors are named `app` and `os`; the App flavor has a normal launcher entry point, while only the OS flavor declares the HOME intent. Both use minSdk 19 and share the same application code.

## Signing and updates

The checked-in build configuration creates debug builds. Debug APKs are suitable for testing and the current local update path, but they are not a production signing strategy. Android only accepts an in-place update when the APK has the same application ID and signing certificate as the installed app. Protect and back up the key used for any long-lived installation before distributing updates. Do not uninstall an existing OS installation to work around a signature mismatch, because uninstalling removes its app data.

## Known limitations

- Hardware verification has primarily used the Xperia E4g E2003 on Android 4.4/API 19. Newer Android releases and a wide range of screen sizes still need device testing.
- Kodi discovery depends on network multicast and Kodi service announcements. Manual connection is the fallback.
- HTTP JSON-RPC is not encrypted.
- Artwork and controls depend on the metadata and capabilities reported by Kodi and the active player.
- The OS edition is an Android launcher app, not a custom ROM, and it does not root, unlock, flash, or debloat a device.

## License and support

FarfarRemote source code is licensed under [GPL-3.0](LICENSE). Graphic asset provenance and license notes are in [graphics/README.md](graphics/README.md) and [graphics/SETTINGS_ASSETS.md](graphics/SETTINGS_ASSETS.md).

Optional support: <https://buymeacoffee.com/farfarspelar>.
