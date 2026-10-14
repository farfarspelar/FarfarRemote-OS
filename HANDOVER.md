# FarfarRemote handover

Last updated: 2026-10-14

## Current verified FarfarRemote baseline

- The Xperia currently has the OS `0.4.6-rc5` build installed in place (`org.farfarremote`). Stable v0.4.7 App and OS APKs have since been built with the same signing certificate, but were not installed during release packaging. Both flavors share the same project; App is `org.farfarremote.app`.
- The owner now reports that all current features have been tested and work on both App and OS editions. Earlier checks separately recorded the App on Samsung Android 13 and the OS on Xperia E2003/API 19.
- The active-stream folder browser was additionally checked on the Xperia while Kodi played an episode: it opened the episode's parent folder and restored that folder after returning to the remote. Gestures were injected through ADB for this check.
- Battery life around 12 hours is an informal owner estimate only. No unplugged, controlled endurance measurement has been completed; the current battery tooling correctly rejects USB-powered sessions.
- Root is not verified. The owner reports the bootloader unlocked, but the current standard ADB shell is UID 2000 and the Fastboot unlock query did not provide a result.

## Next phase: exact firmware source and offline ROM analysis

This phase is focused on obtaining a traceable E2003 stock firmware package and analyzing it offline. No root app has been installed and no root, firmware, package, partition, or bootloader change has been made.

### What we found

- The phone is the single-SIM **Sony Xperia E4g E2003**, Android 4.4.4/API 19, firmware `25.0.A.2.31`, customization `1293-7358 R7A`.
- There are historical user reports claiming **KingRoot** worked on an E2003 with firmware `25.0.A.2.31`. One report says root was obtained and then KingRoot was replaced with SuperSU. These are anecdotal reports from 2016, not a repeatable, security-reviewed method. Other E2003 users reported that KingRoot failed. KingRoot and KingoRoot are different tools. See [the exact firmware report](https://4pda.to/forum/index.php?showtopic=668811&st=320) and [the E4g root discussion](https://forum.android.com.pl/topic/234990-xperia-e4g-e2003-e2006-e2053-w%C4%85tek-zbiorowy/223).
- No trustworthy KingRoot APK, exact APK version/hash, or verified sequence for this exact customization has been established. Do not install an APK from a random mirror or run a PC rooting utility.
- Firmware research lists an E2003 `25.0.A.2.31 R10A Customized UK` FTF and an R3A Germany/MEA package. Neither has a verified hash, inspected package metadata, or confirmed match to `1293-7358 R7A`; neither is cleared for restoration or flashing. A similarly named R7A Nextel-PE package is listed under **E2006** and is excluded. Details are in [`research/custom-rom/FIRMWARE_SOURCES.md`](research/custom-rom/FIRMWARE_SOURCES.md).
- Owner says the bootloader is unlocked, but available read-only Fastboot queries did not independently confirm that. Android ADB currently has shell UID, not root.

### Suggested order for the ROM track

1. Obtain a traceable exact E2003 stock package, or at minimum the E2003 R10A UK candidate, and verify its source, archive integrity and contents offline. Do not use it as a restore/flash image unless its model, build and CDA are reconciled. Exclude the R7A Nextel-PE E2006 package.
2. Extract only to a local ignored workspace; inventory `kernel.sin`, `fotakernel.sin`, system and metadata. Record hashes, image sizes, kernel config clues and boot format. Keep proprietary files out of Git.
3. Find the exact 3.10.48 kernel source and defconfig. Compare source revision/configuration with the extracted stock kernel before attempting any build.
4. Establish a recovery route using Sony Companion or an exact stock FTF and document its limitations. The owner reports the bootloader unlocked, but Fastboot has not confirmed this.
5. If those artifacts become trustworthy, run the offline boot-image parser against copies and assess the historical Magisk candidate. This is still research; any on-device root/boot operation needs separate approval and a recovery rehearsal.
6. Keep the working FarfarRemote OS as the control baseline. Do not root, flash, wipe, repartition, disable packages, or write TA/NVRAM/proinfo/protect/secro/tee/seccfg during source research.

### Working-tree state

The active branch is `feature/os-rom-source-hunt`, based on stable release commit `660c634` / tag `v0.4.7`. The stable commit is on `main`; this research work is isolated in the development branch. Root-readiness notes and the read-only `tools/root_readiness.sh` are tracked project research; the full feasibility study is under `research/custom-rom/`. The script does not reboot or write to the phone.

## Current development: Kodi folder browser and per-folder track preferences

This is historical app-development context from the `feature/swipe-browser-language-memory` branch; that branch was consolidated into stable release `v0.4.7` on `main`. Current root/custom-ROM research is in `feature/os-rom-source-hunt`.

### Kodi browser status

Swipe left on the remote opens Settings; swipe right opens the in-app Kodi library browser. From the browser, swipe left returns to the remote and swipe right navigates to the parent. The browser can list sources/folders and launch selected files without opening Kodi's TV-side menus.

Version 0.4.6-rc5 additionally asks Kodi for the active player's file and opens its parent directory first. On the Xperia E2003 with Kodi actively playing an episode, this displayed `Made in Abyss-Season 1` and its episode files. Returning to the remote and reopening the browser restored that folder. The check used ADB-injected swipe events; finger feel was not assessed. If Kodi has no usable active-file directory, the browser falls back to its saved location/source logic.

Kodi's API documents `Files.GetDirectory` and `Player.Open` in the [Kodi JSON-RPC API](https://kodi.wiki/view/JSON-RPC_API/v13.11).

### Per-folder audio/subtitle preferences

The track pickers provide **Remember current for folder** and **Forget folder rule**. Rules are local and match language/name metadata rather than unstable stream indexes. Subtitle Off can be remembered. Kodi controls continue to use the existing JSON-RPC methods.

Both App and OS debug APKs build. The OS v0.4.6-rc5 APK was installed in place on the Xperia without clearing app data. The live Kodi browser path was checked on-device. Per-folder language restoration across multiple episodes, offline fallbacks, and App flavor runtime behavior still need focused regression testing.

### Repository checkpoints

- Repository: `farfarspelar/FarfarRemote-OS`
- App implementation branch: `feature/swipe-browser-language-memory`
- Base commit before the pending changes: `29b8814` — `Fix wordmark wrapping in offline header`
- Stable `v0.4.7` is now on `main`; it was pushed by fast-forward, with no history rewrite.
- The previously installed Xperia OS APK was `0.4.6-rc5`, versionCode 14. Stable 0.4.7 APKs were built and published with the same signing certificate; no install was performed as part of the release packaging.

Root-readiness work is documentation and a read-only shell script only. No rooting, bootloader, firmware, partition, or Android package changes were made. The root research is intentionally in a separate commit from app development.

## Current Power Off behavior

The main screen has a red **Power Off** control in the top-right header, replacing the header Settings gear. The existing Settings buttons lower in the portrait and landscape views remain available. Tapping Power Off asks for confirmation, then calls Kodi JSON-RPC `System.Shutdown` using the existing background I/O executor. The confirmation says that the Kodi device will shut down while the Android remote stays on.

This shuts down the **device running Kodi** (for example, the MeLE computer). It does not shut down the Xperia handset. Kodi's host operating system must permit shutdown, and the Kodi JSON-RPC account must have the `ControlPower` permission. Do not test this by sending the command unless the owner intends to power down the Kodi host.

Historical note: the published v0.4.2-rc1 APKs predate the Power Off feature. Current development source includes the feature; see the README for the latest published-download links and the current source version.

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
4. For the OS optimization track, start from `reports/debloat/DEBLOAT_0.1_PLAN.md`, `FIRMWARE_STRATEGY.md`, and `reports/os/DEVICE_READINESS_2026-10-14.md`. The owner says the bootloader is unlocked. Read-only Fastboot confirmed product E2003 and the matching bootloader/firmware, but `getvar unlocked` returned no value and `oem device-info` is unsupported. Android still runs ADB as `uid=2000(shell)` with no `su` in the checked standard paths. After a read-only reboot to/from Fastboot, FarfarRemote remained the HOME activity and PSS was 7,352 kB in a single post-reboot snapshot. Wi-Fi remained scanning/disconnected even after 13 minutes; ADB shell cannot toggle it (`CHANGE_WIFI_STATE` denied), so the owner must reconnect/check it through Android Settings before Kodi regression is complete. A Phase A dry-run lists seven user apps; all seven were confirmed enabled in the latest read-only package check. Five were previously approved as a first batch. ADB shell `pm disable-user` was denied by this firmware. Android Appinfo for the first candidate offered Force stop and Uninstall, but no Disable action. No package state changed. Do not replace disable with uninstall or use root/system edits until an exact, verifiable, recoverable method is established and the required action is authorized.
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
