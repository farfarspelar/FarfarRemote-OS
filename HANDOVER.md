# FarfarRemote handover

Last updated: 2026-10-14

## Where the work is

- Repository: `farfarspelar/FarfarRemote-OS`
- Current integrated branch: `main`
- Main fast-forwarded from the integrated development history; implementation checkpoint before the latest handover: `5f374b8` — `Note Power Off is not in current RC APKs`
- Current OS work branch: `feature/os-track-continuation`, created from the integrated `main`.
- Integration checkpoint: `integration/os-continuation` at `44ed21d`; it is pushed to `origin`.
- Previous feature commit: `b6865d9` — `Add confirmed Kodi power off control`
- The Power Off feature and release-download naming changes are now in `main`; the integration branch preserves the unified feature history.
- Working tree was clean after the latest push.

The requested development history is now on `main`. Make future changes on a new feature branch from the latest `main`; do not rewrite history or force-push.

## Current Power Off behavior

The main screen has a red **Power Off** control in the top-right header, replacing the header Settings gear. The existing Settings buttons lower in the portrait and landscape views remain available. Tapping Power Off asks for confirmation, then calls Kodi JSON-RPC `System.Shutdown` using the existing background I/O executor. The confirmation says that the Kodi device will shut down while the Android remote stays on.

This shuts down the **device running Kodi** (for example, the MeLE computer). It does not shut down the Xperia handset. Kodi's host operating system must permit shutdown, and the Kodi JSON-RPC account must have the `ControlPower` permission. Do not test this by sending the command unless the owner intends to power down the Kodi host.

The published v0.4.2-rc1 APKs were built before this feature was added. The current `main` source has the feature; a later version/build is needed before it appears in a downloadable APK.

## Verified on the Sony Xperia E4g E2003

- Device detected over ADB as `E2003`, Android 4.4.4/API 19.
- OS APK installed with `adb install -r`; Android reported success, `org.farfarremote`, version `0.4.2-rc1`, versionCode 6, targetSdk 28.
- FarfarRemote MainActivity launched after installation.
- A screenshot after the UI settled showed the new Power Off control in the top-right header, the existing Settings control below, and Kodi connected with media information displayed.
- Installation was an in-place update; the app was not uninstalled and its data was not cleared.
- The actual Power Off confirmation and `System.Shutdown` command were **not** exercised. Shutdown behavior on the MeLE host remains to be verified intentionally.
- The test was visual and used ADB; no physical button tap was performed.

## Downloadable RC artifacts

The v0.4.2-rc1 GitHub prerelease APK assets now include their minimum Android version/API in the filenames:

- `FarfarRemote-App-Android4.4plus-API19plus-v0.4.2-rc1.apk` — min Android 4.4/API 19, target API 36; emulator checks on Android 13 and 15, plus the owner-reported Samsung Android 13 use.
- `FarfarRemote-OS-Android4.4plus-API19plus-v0.4.2-rc1.apk` — min Android 4.4/API 19, target API 28; dedicated HOME launcher verified on Xperia E2003.

The renamed release assets were downloaded again and matched the local SHA-256 manifest. Their APK bytes and version metadata did not change. These prerelease APKs do not contain the later Power Off feature.

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
4. For the OS optimization track, start from `reports/debloat/DEBLOAT_0.1_PLAN.md`, `FIRMWARE_STRATEGY.md`, and `reports/os/DEVICE_READINESS_2026-10-14.md`. The owner says the bootloader is unlocked. Read-only Fastboot confirmed product E2003 and the matching bootloader/firmware, but `getvar unlocked` returned no value and `oem device-info` is unsupported. Android still runs ADB as `uid=2000(shell)` with no `su` in the checked standard paths. After a read-only reboot to/from Fastboot, FarfarRemote remained the HOME activity and PSS was 7,352 kB in a single post-reboot snapshot. Wi-Fi remained scanning/disconnected, so confirm reconnect and Kodi control manually. A Phase A dry-run lists seven user apps; all seven were confirmed enabled in the latest read-only package check. Five were previously approved as a first batch. ADB shell `pm disable-user` was denied by this firmware. Android Appinfo for the first candidate offered Force stop and Uninstall, but no Disable action. No package state changed. Do not replace disable with uninstall or use root/system edits until an exact, verifiable, recoverable method is established and the required action is authorized.
5. Re-run the contract test and build both App and OS APKs after any code change. Install the OS APK with `adb install -r` to preserve the existing app data.

## Useful commands

```sh
git status --short --branch
git log --oneline --decorate -5
python3 tools/test_v03_contract.py
ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleAppDebug assembleOsDebug
adb devices -l
adb install -r app/build/outputs/apk/os/debug/app-os-debug.apk
```

For the established Xperia OS installation, keep the OS flavor (`org.farfarremote`). Do not install the separate App flavor (`org.farfarremote.app`) over it. No root, firmware flash, debloat, or system-package changes were performed as part of this feature. The owner reports that the bootloader was already unlocked; it was not unlocked by this work.
