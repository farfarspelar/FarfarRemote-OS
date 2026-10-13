# FarfarRemote handover

Last updated: 2026-10-14

## Where the work is

- Repository: `farfarspelar/FarfarRemote-OS`
- Current branch: `feature/kodi-power-off-button`
- Current commit: `a61d923` — `Move Power Off to the top header`
- Previous feature commit: `b6865d9` — `Add confirmed Kodi power off control`
- Branch is pushed to `origin`; working tree was clean after the push.
- `main` was not changed or merged.

Continue on `feature/kodi-power-off-button` unless the project owner chooses another branch. Do not merge this feature to `main` without an explicit request.

## Current Power Off behavior

The main screen has a red **Power Off** control in the top-right header, replacing the header Settings gear. The existing Settings buttons lower in the portrait and landscape views remain available. Tapping Power Off asks for confirmation, then calls Kodi JSON-RPC `System.Shutdown` using the existing background I/O executor. The confirmation says that the Kodi device will shut down while the Android remote stays on.

This shuts down the **device running Kodi** (for example, the MeLE computer). It does not shut down the Xperia handset. Kodi's host operating system must permit shutdown, and the Kodi JSON-RPC account must have the `ControlPower` permission. Do not test this by sending the command unless the owner intends to power down the Kodi host.

## Verified on the Sony Xperia E4g E2003

- Device detected over ADB as `E2003`, Android 4.4.4/API 19.
- OS APK installed with `adb install -r`; Android reported success, `org.farfarremote`, version `0.4.2-rc1`, versionCode 6, targetSdk 28.
- FarfarRemote MainActivity launched after installation.
- A screenshot after the UI settled showed the new Power Off control in the top-right header, the existing Settings control below, and Kodi connected with media information displayed.
- Installation was an in-place update; the app was not uninstalled and its data was not cleared.
- The actual Power Off confirmation and `System.Shutdown` command were **not** exercised. Shutdown behavior on the MeLE host remains to be verified intentionally.
- The test was visual and used ADB; no physical button tap was performed.

## Automated checks and build

- `python3 tools/test_v03_contract.py` passed after the layout change. These are source/manifest regression contract checks, not UI interaction tests.
- `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleOsDebug` passed after the layout change.
- Build emitted existing Java 8 source/target deprecation warnings under JDK 21; there were no build errors.
- `git diff --check` passed before commit.
- The OS debug APK installed on the Xperia is `app/build/outputs/apk/os/debug/app-os-debug.apk` (about 1.20 MiB). It is built with the local debug signing key. Do not distribute as a stable upgrade unless the signing-key/update policy is confirmed.
- Build both tracks from the current source with:

  ```sh
  ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleAppDebug assembleOsDebug
  ```

## Next steps

1. On the Xperia, visually confirm the header spacing and that Settings lower on the screen still opens correctly in portrait and landscape.
2. With the owner ready to shut down the Kodi host, tap **Power Off**, inspect the confirmation, and choose Cancel once to verify cancellation does nothing.
3. When it is safe to turn Kodi off, confirm the action and check that the MeLE host shuts down while the Xperia stays on. If it fails, check Kodi's `ControlPower` permission and host OS shutdown configuration; capture the user-visible error without logging credentials.
4. Re-run the contract test and build both App and OS APKs after any code change. Install the OS APK with `adb install -r` to preserve the existing app data.
5. Review the feature diff and commits, then ask the owner before merging to `main` or preparing a public release.

## Useful commands

```sh
git status --short --branch
git log --oneline --decorate -5
python3 tools/test_v03_contract.py
ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleAppDebug assembleOsDebug
adb devices -l
adb install -r app/build/outputs/apk/os/debug/app-os-debug.apk
```

For the established Xperia OS installation, keep the OS flavor (`org.farfarremote`). Do not install the separate App flavor (`org.farfarremote.app`) over it. No root, bootloader unlock, firmware flash, debloat, or system-package changes were performed as part of this feature.
