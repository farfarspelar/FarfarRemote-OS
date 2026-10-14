# FarfarRemote 0.4.6 RC5 — open the active stream's folder

- **PASS (build):** `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleOsDebug assembleAppDebug` built both APKs. OS: `org.farfarremote`, min API 19 / target API 28. App: `org.farfarremote.app`, min API 19 / target API 36. Both are version `0.4.6-rc5`, versionCode 14.
- **PASS (physical update):** Installed the OS APK over the connected Sony Xperia E2003 / Android 4.4.4 (API 19) with `adb install -r`. It accepted the update in place; no uninstall or data clear was performed. Kodi remained connected and active playback status was visible afterward.
- **PASS (physical Kodi browsing via ADB-injected gestures):** With Kodi actively playing an episode, opening the browser showed `Made in Abyss-Season 1` and episode files, derived from the active stream's parent folder. Returning to the remote and reopening the browser showed the same folder again. This exercises the actual Kodi JSON-RPC path and API 19 device; swipe feel was not assessed with a finger gesture.
- **PASS (fallback behavior, code/build):** When active playback metadata is unavailable or its parent folder cannot be listed, the browser continues with the saved folder/source path. A failed stale saved-folder lookup no longer saves the source fallback over the prior preference.
- **PASS (package identity):** OS remains `org.farfarremote`; App remains `org.farfarremote.app`. Both retain minSdk 19. OS targetSdk remains 28; App targetSdk remains 36.
- **NOT TESTED:** Separate App flavor installation/use, modern Android device behavior, Kodi offline/transient failure fallback, and a no-active-playback browser launch were not re-tested in this pass.
- **BUILD NOTES:** Existing JDK 21 / Java 8 source-target and Gradle deprecation warnings remain; build succeeded. `git diff --check` passed. No `FATAL EXCEPTION` was found in the captured device log window.
- **APK SHA-256:** OS `8590ff750a647a6eeb43018dc82a8dbcb6af0e35b1a3de62ea5749962b94777d`; App `1ee26f0f49ed8a8ef23b0e64c49591e040baa86a394d23bc6cfc3c8a2b072948`.

# FarfarRemote 0.4.6 RC4 — remember the last Kodi folder

- **PASS (build):** Both App and OS debug APKs assembled with Gradle. App ID `org.farfarremote.app` / target API 36; OS ID `org.farfarremote` / target API 28; both min API 19. Version 0.4.6-rc4 / versionCode 13.
- **PASS (physical update):** Installed OS APK on Xperia E2003 / Android 4.4.4 (API 19) with `adb install -r`; versionCode 13 is installed and the existing package/data were retained.
- **CHANGE:** Remember the last successfully listed folder or source in existing app preferences. Reopening Kodi Library restores that location instead of querying Kodi's changing GUI folder after playback. Navigation updates the saved location only after a successful listing; a stale saved path falls back to video sources.
- **PASS (physical location retention):** On the Xperia, opened Kodi video sources, entered `Videos`, swiped back to the remote, then reopened the library. It restored `Videos` rather than re-reading a different Kodi GUI location. The title was read on screen; preference contents/paths were not logged.
- **DEVICE TEST STATE:** The persistence check left `Videos` as the last saved browser folder on this test phone. The new build will remember the next folder successfully opened; navigate to `Anime` once to make that the restored folder.
- **LIMITATION:** The exact `Anime`-after-playback path was not reproduced in this check; confirm it with the owner’s normal Anime browsing/playback flow. The retained-location flow itself was exercised on the device.
- **APK SHA-256:** OS `6ecddb3521eaa6eca45723034fa41b7e5e8d262e4f3fa48ae3c438c263062419`; App `fe527f67f9276b4e2f2b3317db73960c1feed5447fb5a45398effe166872d772`.

## FarfarRemote 0.4.6 RC3 — Kodi folder request and swipe-back fixes

- **PASS (build):** `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleOsDebug assembleAppDebug` built both variants. App is `org.farfarremote.app`, target API 36; OS is `org.farfarremote`, target API 28; both retain min API 19. Version is 0.4.6-rc3 / versionCode 12.
- **PASS (physical update):** Installed the OS APK on Sony Xperia E2003 / Android 4.4.4 (API 19) with `adb install -r`. Android reports versionCode 12 and target API 28. Existing and new APK signer SHA-256 fingerprints match: `63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`. No uninstall or data clear was performed.
- **PASS (live Kodi JSON-RPC):** Using the saved endpoint without printing its address or credentials, `XBMC.GetInfoLabels` returned a current folder and `Files.GetDirectory` returned 13 items in both `media: video` and `media: files` modes when optional `properties` were omitted. The old request shape with those extra properties was the source of Kodi's `Invalid params` response.
- **CHANGED:** Reduced swipe distance threshold to 44 dp. Swipe right in Settings returns to the remote. Swipe left from Kodi Library returns to the remote; swipe right navigates to the parent folder (and exits at the root). Text fields retain horizontal editing gestures. Simplified `Files.GetDirectory` parameters to avoid Kodi-version schema rejection.
- **PASS (physical UI via ADB input):** On the Xperia, an injected right swipe opened the current Kodi folder and displayed episode entries; a right swipe navigated to the parent folder; a left swipe returned to the remote. A right swipe from Settings also returned to the remote. This verifies gesture routing on the real API 19 screen, though finger feel was not evaluated with a physical swipe.
- **APK SHA-256:** OS `250e8b9e2faf7844c763069fa07193dc05b5d173234f0e9955d6156bec1edbcb`; App `198ec8b63fdfd3ea2a6c843e5da5e947fad0f00ee30b3e30206c2570a10643d2`.
- **BUILD WARNINGS:** Existing JDK 21 / Java 8 source-target and deprecated API warnings remain; both assemblies succeeded.

## FarfarRemote 0.4.6 RC1 — swipe browser and per-folder track preferences

- **PASS (build):** `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleOsDebug assembleAppDebug` assembled both variants. App metadata: `org.farfarremote.app`, versionCode 10 / `0.4.6-rc1`, min API 19, target API 36. OS metadata: `org.farfarremote`, same version, min API 19, target API 28.
- **PASS (signing metadata):** Both debug APKs verify and have the same local debug certificate fingerprint as the existing development key: `63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`. This is not a production release signature.
- **PASS (manifest inspection):** App has the ordinary `MAIN` + `LAUNCHER` entry and no HOME category; OS retains `MAIN` + `HOME` + `DEFAULT`.
- **PASS (repository hygiene):** `git diff --check` passed.
- **NOT RUN:** Automated behavioral tests were not added or run for this feature.
- **PASS (device install):** Installed the OS APK on the connected Sony Xperia E2003 as an in-place update using `adb install -r`. The installed package reports `org.farfarremote`, versionCode 10 / `0.4.6-rc1`, target API 28. The installed and new APK signing certificate SHA-256 fingerprints match (`63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`). No uninstall or data-clear was performed, so Android preserved the existing app data during the update.
- **NOT VERIFIED ON DEVICE:** Swipe navigation, current-folder detection, folder/source listing, playback launch, saved language matching on the next episode, subtitle Off restoration, and behavior with live Kodi remain to be tested together with the owner.
- **KNOWN BUILD WARNINGS:** Existing JDK 21 warnings for Java 8 source/target and deprecated APIs remain; both APK assemblies succeeded.
- APK SHA-256 — OS: `35558a8d1719a59cc7697403f9ed6e4d5acef72d7b7b829cfdbc9a892fc4ac9f`.
- APK SHA-256 — App: `1b5b7a6002b135cf8286efc99c4f8413f3d126546690eac2e715f9233bc32f64`.

# UI follow-up — FarfarRemote wordmark wrapping

- **CHANGE:** Prevented the header wordmark from wrapping when the longer startup/offline status competes for width. The wordmark is one styled, single-line `TextView`; the status and host labels are single-line and capped, and startup uses the compact offline status. No orientation policy or Kodi code changed.
- **PASS:** Both App and OS variants rebuilt; source-contract regressions for the wordmark, Kodi behavior, favorites, and OS battery behavior passed. `git diff --check` passed.
- **PASS:** The OS APK was installed over the Xperia E2003 installation with `adb install -r`. The old and new APK signing certificate SHA-256 fingerprints match; package ID, versionCode, and saved preferences are retained.
- **APK SHA-256:** App `2933f16881595f50bfa9222fb0a7845189ad171b2fe3b1a6e94a3d42338c5462`; OS `0fdb56c9ed60bdcb877ad0e21c29d53a6b15907e1d8ab0360a128e4bad3169df`.
- **NOT VERIFIED:** The rotation symptom still needs visual confirmation on the Xperia. The app was opened after installation, but the full Settings-to-remote and landscape-to-portrait sequence was not observed by the test operator.

# FarfarRemote OS 0.4.5 RC1 — Battery Optimization Phase 1

- **PASS:** `./tools/build_distributions.sh` built App and OS debug APKs. Metadata checks passed: App `org.farfarremote.app`, target API 36; OS `org.farfarremote`, target API 28; both min API 19, versionCode 9 / versionName `0.4.5-rc1`.
- **PASS:** `tools/test_v03_contract.py`, `tools/test_favorites_contract.py`, and `tools/test_os_battery_contract.py` passed. Gradle `testAppDebugUnitTest` and `testOsDebugUnitTest` are `NO-SOURCE`; the project has no Android unit-test sources.
- **PASS:** The new OS APK was installed over the existing Xperia OS APK with `adb install -r`, without uninstalling or clearing app data. The installed package reports version 0.4.5-rc1. The installed APK's signer matched the new APK before installation (`63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`).
- **PASS:** Device is Android 4.4.4/API 19; installed manifest retains the existing `org.farfarremote` identity and OS HOME activity. Screen timeout remains 30,000 ms. A read-only snapshot later showed Wi-Fi connected while the display was asleep.
- **PASS:** `tools/battery_measure.py` refused to start a measurement because ADB was USB-connected and the phone reported USB power. No USB-powered battery data was treated as endurance data.
- **APK SHA-256 at battery-phase build:** App `e243a39c86bba2a94d94dbaae0ae6e3d88e6448b7132e31a2ab4ad6190742015`; OS `ed008c762d5e45fac8ae4525e5f377d7464c4fc265a54d552ea80f312fea1747`. See the follow-up section above for the rebuilt APK hashes.
- **NOT VERIFIED:** No unplugged baseline or optimized session was captured. No battery improvement, current draw, battery capacity, or 24-hour runtime is claimed.
- **NOT VERIFIED:** The screen remained at Android Keyguard during the attempted wake check, so the new Activity's screen-on/off receiver logs and Battery Mode UI were not runtime-verified on the physical screen. Kodi was not available for command-latency, Audio/Subtitles, Find My Kodi, or post-sleep reconnect checks. Wi-Fi's single connected snapshot is not a reconnection test.
- **LIMITATION:** The Gradle build succeeds with the existing JDK 21 / Java 8 source-target deprecation warnings. There are no new Android permissions, root requirements, system setting writes, package changes, or firmware changes.

# FarfarRemote 0.4.4 RC1 — favorites and release packaging

- **PASS:** Existing v0.3 source-contract regression script and new favorites source-contract script pass.
- **PASS:** Both App and OS debug variants compile and assemble; Gradle unit-test tasks report `NO-SOURCE`.
- **PASS:** Release packaging checks verify App ID `org.farfarremote.app`, OS ID `org.farfarremote`, versionCode 8, versionName `0.4.4-rc1`, minimum API 19, App target API 36, and OS target API 28.
- **PASS:** APK SHA-256 files are generated and checked against the APK bytes.
- App SHA-256: `0c53d483a133f0a1f7f9e91117c54fedf8dddaf553fc11800f835db14e6a07fc`.
- OS SHA-256: `a6d1c3e19c63037d36f20387784b88c10b321034dc3ba880edbc7fcf659b18da`.
- **PASS:** The OS APK signing certificate fingerprint matches the locally retained v0.4.3 OS APK (`63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`), preserving its in-place update signing path.
- **NOT VERIFIED:** No Kodi host is available in this work session, so saving and reopening a real Kodi folder favorite is not behavior-tested. Favorites still require physical Kodi verification.
- **NOT VERIFIED:** No update install was performed on the Xperia in this release build. The OS package ID and debug signing setup remain unchanged; confirm the certificate fingerprint matches the installed build before installing over it.

# Current development work — folder favorites and Home/Stop artwork

- **PASS:** Existing `python3 tools/test_v03_contract.py` regression contract checks; protected layout builders, Kodi client, remote actions, existing preference keys, and distribution manifests remain unchanged.
- **PASS:** `tools/test_favorites_contract.py` checks the opt-in capture action, Kodi folder path retrieval, local persistence, launch-window path use, removal, and localized Home/Stop edge clipping. This is a source contract check, not a Kodi behavior test.
- **PASS:** `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug`. Both debug variants compile and assemble; Gradle unit-test tasks are `NO-SOURCE`. The existing JDK 21 Java 8 source/target warnings remain.
- **PASS:** APK metadata check reports App `org.farfarremote.app` and OS `org.farfarremote`; both remain versionCode 7/versionName `0.4.3-rc1`, minSdk 19; App targetSdk 36 and OS targetSdk 28.
- **PASS:** The OS favorites test APK's signing-certificate SHA-256 matches the existing local v0.4.3 OS APK (`63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`). Device-side in-place update was not run.
- **NOT VERIFIED:** No Kodi/MeLE host is reachable in this work session. A real `XBMC.GetInfoLabels` response, save flow, `GUI.ActivateWindow` folder navigation, and operation with multiple Kodi content types must be tested with Kodi. No physical device was changed or flashed for this task.
- **NOT VERIFIED:** Touch appearance and clipping on the Xperia display; both APKs have only been compiled here. The generated APK outputs are in the Gradle build output directories and are not a new public release.

# FarfarRemote 0.4.3 RC1 — display timeout verification

## Change

- The Xperia system screen timeout was read as **30,000 ms**. FarfarRemote had been overriding it because `keep_awake` defaulted to `true` in both the activity behavior and Settings presentation.
- Changed only the fallback value to `false`; the existing `keep_awake` preference key remains unchanged. The existing switch still opts in to `FLAG_KEEP_SCREEN_ON` when enabled. With the override off, Android's configured screen timeout applies (30 seconds on the checked Xperia; other phones use their own system timeout).
- Kodi client, remote controls, HOME manifests, orientation handling, application IDs, minimum SDK, and saved Kodi preference keys are unchanged.
- **PASS:** `tools/build_distributions.sh` and `python3 tools/test_v03_contract.py`; both APK flavors compile and assemble. Unit-test tasks are `NO-SOURCE` because there are no unit-test source files. Existing JDK 21 warnings for Java 8 source/target remain.
- **PASS:** APK metadata: App `org.farfarremote.app`, OS `org.farfarremote`, both versionCode 7 / versionName `0.4.3-rc1` / minSdk 19; App targets 36 and OS targets 28.
- **PASS:** `adb install -r` updated the Xperia OS package in place; Android reported version 0.4.3-rc1 and FarfarRemote was selected again as the HOME activity. The preference file could not be read by ADB `run-as` (permission denied); no uninstall or data clear was performed.
- **PASS:** On the physical Xperia, system timeout remained 30,000 ms. After 35 seconds without input, `dumpsys power` reported `mWakefulness=Asleep`, `mScreenOn=false`, and `mWakeLockSummary=0x0`. Waking and swiping back returned to FarfarRemote HOME.
- **NOT VERIFIED:** Kodi reconnection and control after this update; Wi-Fi was still `SCANNING/DISCONNECTED`. App APK was built and metadata-checked but not installed on a second device in this task.
- SHA-256: App `c1c7f216b66a253961b9200ee36b0cd2de7fc0aa3adcf760d9d09b03e1ed94ca`; OS `74aabf653bf31c4367d9077d3975ef2b8c476fd289aec16c87126220c3d44ec4`.
- Artifacts: `dist/FarfarRemote-App-Android4.4plus-API19plus-v0.4.3-rc1.apk`, `dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.3-rc1.apk`, and `dist/SHA256SUMS-0.4.3-rc1.txt`.

## Prior release-track QA: 0.4.2 RC1

**Branch:** `feature/release-track-split`  **Base:** `9232787` (FarfarRemote 0.4.1 RC1)

## SDK strategy

- Both variants compile against API 36 and retain `minSdk 19`. This retains the established OS device range, and the modern App APK was also installed and launched on the API 19 Xperia to verify the low-minimum package can load there. New framework APIs are isolated in API-specific helper classes and guarded by runtime version checks.
- App (`org.farfarremote.app`) targets API 36. This adopts current Android behavior and meets the current Google Play target requirement for new apps and updates; the repository distributes GitHub APKs and does not depend on Play. Android 15+ edge-to-edge insets and Android 13+ Settings Back handling are App-only.
- OS (`org.farfarremote`) stays target API 28, min API 19, and retains HOME intent and application ID for the Xperia reference installation. The conservative target is deliberate compatibility policy.
- Both variants continue allowing cleartext HTTP because Kodi's configured JSON-RPC endpoint uses HTTP. This is a known transport limitation: credentials and commands are not encrypted.
- Android 17/API 37 is not targeted. Apps targeting API 37 need the local-network permission or a system-mediated discovery path; future work must update and test direct connections plus DNS-SD discovery before changing target.

## Automated/build checks

- **PASS:** `python3 tools/test_v03_contract.py`. It checks protected Kodi/control methods against the v0.2 reference, flavors, manifest intent categories, IDs, API split, guards, and existing preference keys. This is a source/manifest contract check, not a behavioral test.
- **PASS:** `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug` with Gradle 8.13, AGP 8.13.2, Platform 36, Build Tools 35.0.0. App and OS compilation/assembly passed. Unit-test tasks report `NO-SOURCE`; this repo has no Android unit-test sources. Java 8 source/target on the JDK 21 build runtime emits the existing deprecation warning.
- **PASS:** `tools/build_distributions.sh` validates application IDs, versions, and target SDK metadata, then emits both APKs and SHA-256 sidecars/manifest.
- **PASS:** Android manifest inspection confirms App `MAIN`/`LAUNCHER` and no HOME intent; OS retains `MAIN`/`HOME`/`DEFAULT`. App opts into platform predictive-back callbacks.

## Physical E2003 checks

The attached Sony Xperia E4g E2003 runs Android 4.4.4/API 19.

- **PASS:** OS APK updated in place from v0.4.1 RC1 to v0.4.2 RC1 (`org.farfarremote`, versionCode 6, targetSdk 28). `adb install -r` succeeded and HOME resumed the existing FarfarRemote OS activity.
- **PASS:** the OS preferences-file SHA-256 before and after update remained `dacd95c0d0e49155b7032d899b6a0fedcada1d0a9d23f900163d8b4d7f2df862`. No preference values were printed.
- **PASS:** OS RC APK signing certificate matches v0.4.1 RC1 and the installed update path. No uninstall, data clear, firmware action, or system-package change occurred.
- **PASS:** App target API 36 installed beside the OS as `org.farfarremote.app` on API 19 and launched successfully. This checks APK installation, manifest parsing, app-class loading, and the guarded modern API code on the legacy OS. Settings and the manual host field opened; Android Back closed Settings and kept the App activity in the foreground. Android Home then returned to the pre-existing OS HOME launcher. The App did not take HOME.
- The OS UI displayed its Kodi-connected indicator after update. Kodi credentials were not copied from the OS install into App for testing. Kodi controls, manual connection tests, and media/audio/subtitle commands were not reissued during this run. A Find My Kodi search was started on the E2003, but the result/candidate state could not be confirmed reliably from the UI inspection and is counted as not verified for this RC. The shared discovery implementation and Settings preference keys are unchanged. The user has previously verified the Kodi and discovery features on the Xperia; do not treat that as a fresh v0.4.2 functional test.

## Modern Android test status

- **PASS (Android 13/API 33 emulator):** installed the API 36 target App APK (`org.farfarremote.app`, min API 19) and launched `MainActivity`. The emulator's HOME query returned only Android launcher activities; FarfarRemote App did not register as HOME. Android Back from Settings returned to the remote screen, and Android Home returned to the emulator's normal launcher. The Settings screen and the manual Kodi fields rendered. No FarfarRemote App crash or App ANR was recorded.
- **PASS with network limitation (Android 13/API 33 emulator):** Find My Kodi ran on user request and ended with the expected “No Kodi found” guidance. The emulator did not discover a Kodi endpoint on its bridged network, so discovery of a real service, endpoint verification, authentication, and saving a selected result were not verified in this run. No existing connection was overwritten.
- **PASS (Android 15/API 35 emulator):** installed and launched the same API 36 target App APK. Status and gesture-navigation bars remained visible, Settings opened, and focusing the manual host field showed the software keyboard while the field remained visible. Back hid the keyboard, the next Back closed Settings, and a side-swipe Back gesture also returned to the remote screen. Android Home returned to the standard launcher. No App crash or App ANR was recorded. The emulator used a standard Pixel 2 profile without a display cutout; this does not cover OEM-specific UI behavior.
- **User-reported physical check:** after the API 33/35 emulator checks, the user confirmed FarfarRemote App works without problems on a Samsung phone running Android 13. The exact feature-by-feature test list and APK build identifier were not provided, so this is recorded as a user report, not an ADB-observed test. The earlier report named a Samsung SM-A715F; this confirmation did not restate the model.
- Android 16/API 36 physical-device behavior, OEM-specific display cutouts, a real Kodi HTTP session on the emulator, and large-screen behavior remain **unverified**. API 35 emulator coverage verifies target-SDK edge-to-edge handling and keyboard insets on a standard profile. An earlier API 36 emulator-image installation attempt ran out of disk space before booting; it was cleaned up. The API 33 and 35 emulator images were successfully booted for their checks. During API 33's first cold start, Android System UI briefly showed an “isn't responding” dialog; after startup settled, App navigation and Settings checks completed, and ActivityManager reported no App ANR.
- API 36 remains below the API 37 local-network permission enforcement. NSD uses the existing user-triggered Kodi DNS-SD service type and the existing explicit confirmation before saving.

## Asset provenance

The owner reports that FarfarRemote UI artwork and visual references were generated with ChatGPT from owner-written prompts and visual direction. This statement is recorded in [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md), the English README, and the graphics documentation. The resources were checked for official Kodi or Buy Me a Coffee logos; none were identified. The coffee cup is generic generated FarfarRemote artwork.

## Current RC artifacts

- `dist/FarfarRemote-App-Android4.4plus-API19plus-v0.4.2-rc1.apk` — target API 36, minimum Android 4.4/API 19.
- `dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.2-rc1.apk` — target API 28, minimum Android 4.4/API 19; Xperia E2003 dedicated-device track.
- SHA-256 sidecars and combined manifest are alongside the APKs in `dist/`.

---

# FarfarRemote 0.4.1 RC1 — QA report

**Date:** 2026-10-13  **Branch:** `release/0.4.1-rc1`  **Base commit:** `3540884` (`feature/two-track-distribution`, v0.4.0)

## Baseline and scope

- The repository was clean at the base commit before RC work; the v0.4.0 tag and development branch both pointed to `3540884`. Existing working changes are isolated on this release branch.
- Before edits, `python3 tools/test_v03_contract.py` passed. `testAppDebugUnitTest` and `testOsDebugUnitTest` both reported `NO-SOURCE`; the App and OS debug assemblies passed.
- The only application logic change is lifecycle gating for the existing Kodi status poll in `MainActivity`: polling starts in `onStart`, is stopped and callbacks removed in `onStop`, and resumes when the activity returns. This addresses measured requests continuing while the regular App sat in the background. KodiClient, discovery, controls, Settings, preference keys, orientation logic, and manifests were not rewritten.
- Version metadata is `0.4.1-rc1` / versionCode 5; minSdk 19 and targetSdk 28 remain. IDs remain `org.farfarremote.app` and `org.farfarremote`.

## Automated and build verification

- **PASS:** updated `python3 tools/test_v03_contract.py` distribution and protected-code checks. These are static source/manifest contracts, not user-interaction tests.
- **PASS:** `./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug`; both assemblies succeeded. Unit-test tasks have no test sources (`NO-SOURCE`). JDK 21 reports the existing Java 8 source/target deprecation warning.
- **PASS:** `tools/build_distributions.sh` validates package IDs and version metadata and creates both APKs and the SHA-256 manifest.
- **PASS:** API metadata: minSdk 19, targetSdk 28. Merged App manifest includes `MAIN`/`LAUNCHER` and has no HOME category; OS has `MAIN`/`HOME`/`DEFAULT`.
- **PASS:** App and OS are separately installable by distinct IDs. Both debug APKs have the same local debug signer. OS RC signer certificate SHA-256 matches the 0.4.0 OS APK: `63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`.

## Physical E2003 checks

The attached device identified as Sony E2003, Android 4.4.4/API 19. The OS flavor was already installed at 0.4.0.

- **PASS:** installed App RC beside the OS package and launched `org.farfarremote.app`. Ordinary status/navigation bars are visible. Pressing Android HOME returned to `org.farfarremote/.MainActivity`, not the App flavor. This confirms App install/launch and HOME separation on API 19; a broad test across phone vendors was not possible.
- **PASS:** installed OS RC over the existing OS package using `adb install -r`; package reported versionCode 5/versionName `0.4.1-rc1`, and Android HOME resumed FarfarRemote OS. No uninstall or data clear occurred.
- **PASS:** the private preferences file SHA-256 before and after OS update was unchanged: `dacd95c0d0e49155b7032d899b6a0fedcada1d0a9d23f900163d8b4d7f2df862`. Values were not printed. This verifies data preservation for the existing update.
- **PASS:** App lifecycle polling observation: a pre-fix live warning log produced polling-related log entries while backgrounded; with RC1 the live log had a gap while HOME/backgrounded and the regular interval resumed when the App returned. The test used an empty App-flavor Kodi host, so the messages were expected connection errors; no credentials or Kodi state were changed.
- **PASS:** one App launch sample after force-stop/start reported `TotalTime: 441 ms`. One `dumpsys meminfo` sample reported total PSS of **13,456 kB**. These are single snapshots, with no equivalent controlled 0.4.0 baseline, so they are not evidence of a speed or memory improvement. CPU samples were contaminated by build/install/package-manager activity; idle CPU is not claimed.
- Screenshots in `docs/screenshots/` show the App variant offline. No host, user name, password, or private network address is included.

## Regression coverage and what was not re-run

The user’s previous manual E2003 verification covers Kodi connection, HOME launcher, portrait/landscape/Auto, volume, audio stream and subtitle stream selection, and Find My Kodi. Version 0.4.0's test report records physical Find My Kodi discovery and explicit save confirmation. The RC contract test checks protected implementation and distribution declarations; no automated behavioral Android tests exist.

During RC validation, no Kodi was configured in the separate App install. Therefore D-pad, media commands, volume/mute, Now Playing/artwork/seek, audio/subtitle changes, Kodi discovery including multiple/failing endpoints, Settings save/test, Buy Me a Coffee launch, and real network interruption were **not** functionally re-run on the RC APK. The protected Kodi code was not changed. Physical sensor rotation, charger/USB behavior and Bluetooth were not re-tested.

No Android emulator or newer Android device was available. The App may run on newer releases, but compatibility across modern Android devices is not verified. Current target SDK is 28; when raising target SDK, review edge-to-edge/insets behavior and newer local-network permission requirements for NSD. See [Android 15 behavior changes](https://developer.android.com/about/versions/15/behavior-changes-15), [Android 17 behavior changes](https://developer.android.com/about/versions/17/behavior-changes-17), and [NsdManager](https://developer.android.com/reference/android/net/nsd/NsdManager).

## Release readiness and known limits

- The release APKs use the local debug signing key, which is not in Git. A stable public release needs an explicit long-term signing key/backup/update policy. Do not change the signing certificate for existing `org.farfarremote` installs.
- The Settings asset pack has an unresolved independent license/provenance statement; review `graphics/SETTINGS_ASSETS.md` before redistributing those third-party supplied assets in a stable public release.
- Kodi HTTP JSON-RPC is unencrypted. Use only on a trusted LAN.
- The landscape first viewport has a scrollable control area; lower controls may require scrolling on the 540×960 device.
- No root, bootloader unlock, firmware flash, system package disable/removal, debloat, bootanimation or system partition change was performed.

## RC artifacts

- `dist/FarfarRemote-App-v0.4.1-rc1.apk` — regular Android app (`org.farfarremote.app`).
- `dist/FarfarRemote-OS-v0.4.1-rc1.apk` — dedicated HOME launcher (`org.farfarremote`).
- `dist/SHA256SUMS-0.4.1-rc1.txt` — combined checksums; each APK also has an adjacent `.sha256` sidecar.
- APK sizes are approximately 1.21 MB each.

---

# FarfarRemote OS — build and test report

## Power Off control — development branch

- Added one shared main-screen Power Off control for both App and OS flavors. It now occupies the top header position previously used by Settings; the existing Settings controls remain available lower in the main view.
- The confirmation explains that the Kodi device will shut down while the Android remote remains on. Confirming sends `System.Shutdown` using the existing background Kodi client; a denied or unsupported request is reported without crashing. The command is Kodi's documented `ControlPower` method.
- The implementation was not exercised against the physical MeLE/Kodi host in this environment. Verify that Kodi's host OS allows power-down and that the Kodi JSON-RPC account has `ControlPower` permission before relying on it.
- Shutting down the Android handset from a regular app is not part of this control; Android 4.4 does not expose a public app-level power-off API.

## 0.2.0 baseline

**Target:** Sony Xperia E4g E2003, Android 4.4.4/API 19, firmware 25.0.A.2.31, 540×960 at 240 dpi. **No root, bootloader, system image or package debloat was performed.**

### Automated and local checks

- `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleDebug` — **PASS**. The temporary SDK had Platform 34 and Build Tools 34.0.0. Java 8 source/target deprecation warnings are from the JDK 21 build runtime; compilation succeeded.
- `aapt dump badging app/build/outputs/apk/debug/app-debug.apk` — **PASS**: package `org.farfarremote`, versionCode 2/versionName 0.2.0, min SDK 19, target SDK 28; HOME launcher activity and INTERNET/ACCESS_NETWORK_STATE/VIBRATE permissions present.
- No third-party Gradle dependencies and no Google Play Services integration.
- PNG sources were inspected for RGBA/alpha and dimensions. The three sheets were split to five/four/four separate buttons; original PNGs are preserved in `graphics/originals/` and `FarfarRemote_Asset_Pack/`.
- The deliverable APK is **1,103,128 bytes (about 1.05 MiB)**. Its SHA-256 matches the Gradle output APK.

### Physical Xperia checks

ADB confirmed the connected target as Sony E2003, build `25.0.A.2.31`, API 19. The device serial is omitted from this report.

- Installed app before test: 0.1.0/versionCode 1. Ran `adb install -r dist/FarfarRemote-0.2.0-api19-debug.apk` — **PASS**, update succeeded in place. It retained the same package and signing identity.
- Shared-preferences file SHA-256 immediately before and after that update was identical (`47138767cd81ec7b03ed8de44ec868017035e26eb0f4442d5b78352457d33c47`). No preference values were printed. Later orientation testing changed only the saved orientation key and left Portrait selected.
- Launched `org.farfarremote/.MainActivity` — **PASS**: activity remained resumed and no fatal app exception appeared in the captured logcat window.
- Opened Settings using the screen, selected Landscape, confirmed Android reported landscape configuration; selected Portrait, confirmed portrait configuration and saved `orientation=portrait`. Selected Auto and confirmed it saved; the device stayed in portrait while tested. Sensor-driven rotation after physically turning the handset remains a manual check.
- Pressed the on-screen Settings control again after rotating and used the Settings UI — **PASS**.
- Opened Android Wi-Fi Settings from FarfarRemote Settings and returned using Back — **PASS**. This gives network credential entry a fallback path when Kodi is offline.
- Settings “Test connection” to the saved Kodi endpoint — **PASS**; response reported connected. This exercises the actual phone-to-Kodi JSON-RPC path (`JSONRPC.Ping` and `Application.GetProperties`). No playback-changing Kodi command was issued during the test.
- Current FarfarRemote process measurement after returning to the remote: **18,100 kB PSS**, **61,960 kB RSS**, **26 threads**, one `top` sample at **0% CPU**. This is a single warm-idle snapshot, not an average or an improvement comparison. The 0.1 baseline for this device/app was not captured in this run.

### Still requires manual verification

- Rotate the physical phone with Auto selected and verify both layouts in normal use.
- Test D-pad directions/OK, each transport/navigation/category touch target and key/HID input against Kodi. ADB touchscreen taps confirmed UI interaction, but the whole remote map was not exercised.
- Play a video with multiple audio and subtitle streams; verify metadata, alternative names, selected flags, Off, poster, episode fields and seek. Current Kodi test verified connection only, not media switching.
- Verify progress polling/seek support on the active player, mute/volume behavior and reconnection after a real Wi-Fi/Kodi outage.
- Verify Bluetooth, charging/wake, sustained memory/CPU and cold boot. No device reboot or charger/Bluetooth regression was run.
- Test offline Settings by disabling Kodi or joining a network with no Kodi host. The code keeps Settings local and handles timeout/auth/address failures, but this was not simulated on the phone.
- Splash uses a first-render overlay with no fixed sleep. Its exact visible duration and appearance need visual check on device; screenshot export was unavailable in this ADB session.

### Debloat gate

Do not debloat yet based only on this app test. First use 0.2 as the selected HOME remote, confirm Wi-Fi text input/recovery and ADB APK install, then take a steady-state baseline. The recommended first system trial is **Phase A only**, and only after FarfarRemote stability verification. Its first default five-package batch is:

1. `app.gpsme` — GPSME navigation app
2. `com.facebook.katana` — Facebook
3. `com.mobisystems.office` — Office editor
4. `com.navigon.navigator_select_sony_eu` — NAVIGON
5. `com.scee.psxandroid` — PlayStation companion app

Use the dry-run plan first and then explicit `--apply --approve-phase A`; follow the script's typed confirmation and complete every regression prompt. Reboot and compare active and cached PSS separately before the second A batch. A/B/C/D remain reversible per user 0; no root or `/system` changes.

## 0.3.0 Settings redesign

**Baseline:** branch `main` was clean except for the supplied, untracked Settings asset folder and its ZIP. The stable v0.2 commit is `a840155`; local tag `v0.2.0` points to it. The pre-change `assembleDebug` passed. Gradle reported no unit-test source (`testDebugUnitTest NO-SOURCE`).

### Build and automated checks

- `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew testDebugUnitTest assembleDebug` — **PASS**. The Java compiler reports existing Java 8 source/target deprecation warnings under JDK 21; compilation succeeds. The Gradle unit-test task is still `NO-SOURCE`.
- `python3 tools/test_v03_contract.py` — **PASS**, 37 checks. It compares the Kodi client and the protected D-pad, remote action, audio/subtitle, orientation-policy and snapshot methods to the v0.2 baseline, and checks app identity, HOME support, API 19, preference keys, support-link handling and Settings selectors.
- `aapt dump badging` — package `org.farfarremote`, versionCode 3/versionName 0.3.0, minSdk 19, targetSdk 28.
- APK size: **1,240,042 bytes**. Debug signer certificate SHA-256 is identical to the v0.2 APK: `63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`.

### Physical E2003 checks

ADB confirmed a Sony E2003 running firmware 25.0.A.2.31/API 19. Installed v0.2 with its same signer, then updated to v0.3 using `adb install -r`. The `shared_prefs/farfarremote.xml` SHA-256 was identical immediately before and after the v0.2→0.3 update. Values were not printed.

- **PASS:** v0.3 starts as `MainActivity` and continues to show Kodi's current connection/Now Playing/track state.
- **PASS:** Settings opens without a final-build crash. The first API 19 run exposed a `Switch.setShowText` `NoSuchMethodError`; that API 21-only call was removed before the final APK. The final Settings open/toggle checks did not create a new crash report.
- **PASS:** Host, port, username and masked password fields render; tapping the host field opens the Android keyboard while keeping the focused field visible. No text was entered and the preferences checksum remained unchanged.
- **PASS:** Test Connection returns `Connected · Kodi` on the existing saved endpoint.
- **PASS:** Android Wi-Fi Settings opens; Back returns to FarfarRemote and its Settings screen.
- **PASS:** pressing system HOME displayed Android's launcher chooser; FarfarRemote was selected with “Always”, and a second HOME press returned to `MainActivity`. FarfarRemote is now the default HOME app, matching the dedicated-device goal.
- **PASS:** Portrait, Landscape and Auto choices each save; the original Auto value was restored after the layout check. The view remains alive across the orientation setting changes. Physical sensor rotation was not tested in this session.
- **PASS:** Password control changes its label to Hide when revealed and back to Show when masked. It was left masked.
- **PASS:** Buy Me a Coffee launches Chrome through Android's external URL handler. No payment page was interacted with. The no-browser clipboard fallback was code/contract checked, not simulated on the phone.
- **PASS:** Returned from Chrome to the same FarfarRemote Settings activity.

### Regression scope and limits

KodiClient, D-pad, play/stop/navigation/volume/seek/track selection methods, launcher manifest, and orientation policy are unchanged from v0.2; the contract test confirms this at source level. The active Kodi screen still displayed the existing paused media item, track labels and progress after update. This session did not send playback, seek, volume, audio-track or subtitle-track commands. Those functions were manually verified by the user on v0.2 and were deliberately not exercised again.

An on-device Settings-screen sample reported **20,123 kB PSS**. The v0.2 report's **18,100 kB** was a separate warm-idle remote-screen sample, so they are not a valid same-state comparison and do not isolate the PNG memory cost. The supplied screen backgrounds are only 540×960/960×540; selected source icons are reduced from 128×128 to 64×64. There are no new runtime libraries, ongoing animations or network polling while Settings is open.

Not re-tested: Wi-Fi loss/reconnect, Kodi-offline errors, no-browser fallback, haptic hardware behavior, a real physical sensor turn in Auto, cold boot, or the complete transport/D-pad command map. The device remained connected to Kodi during the test. No root, debloat, package disabling, bootloader or firmware operation was performed.
# FarfarRemote 0.4.0 — two-track build and Kodi discovery

**Date:** 2026-10-13
**Branch:** `feature/two-track-distribution`
**Baseline:** stable v0.3.0 at `d73a8b0`, after v0.2 baseline `a840155`.

## Automated checks

- **PASS:** v0.3 regression contract passed in a detached, clean worktree before implementation.
- **PASS:** updated source contract confirms the protected Kodi client and remote-control methods are byte-for-byte unchanged from v0.2. It also checks API 19, both application IDs and flavor intent filters, saved preference keys, discovery type, confirmation and timeout/lifecycle cleanup.
- **PASS:** `testAppDebugUnitTest`, `testOsDebugUnitTest`, `assembleAppDebug` and `assembleOsDebug` completed. Gradle reports no unit test sources (`NO-SOURCE`); the Python contract test provides the automated regression assertions.
- **PASS:** `aapt dump badging` reports both APKs at versionCode 4/versionName 0.4.0/minSdk 19. App package is `org.farfarremote.app`; OS package remains `org.farfarremote`.
- **PASS:** merged manifests show App has `MAIN` + `LAUNCHER` and no `HOME`; OS has `MAIN` + `HOME` + `DEFAULT` and no app-flavor identity.
- **PASS:** OS v0.4 APK signer SHA-256 matches the v0.3 debug APK signer.

## Physical Xperia E2003 checks

- **PASS:** updated the existing OS package on the attached E2003 with `adb install -r`. It reports version 0.4.0 and continues to open as the selected HOME activity.
- **PASS:** the `farfarremote.xml` preference file SHA-256 remained `dacd95c0d0e49155b7032d899b6a0fedcada1d0a9d23f900163d8b4d7f2df862` before and after both OS updates. No preference values were logged or changed.
- **PASS:** OS remains connected to the existing Kodi endpoint and displays current Now Playing state after update. No playback or volume command was issued.
- **PASS:** Find My Kodi discovered one Kodi instance through `_xbmc-jsonrpc-h._tcp.`. Selecting it passed `JSONRPC.Ping` and `Application.GetProperties`; the explicit Use and Save confirmation appeared. Canceling it left the settings hash unchanged.
- **PASS:** installed App beside OS on the same E2003. Android installed it as a separate package and direct launch opened it. Its normal Android status/navigation bars were visible. Pressing Android HOME returned to the existing OS launcher. Removed only the temporary `org.farfarremote.app` test install afterward; `org.farfarremote` stayed installed as v0.4.0.
- **PASS:** the App flavor's debug APK and OS flavor's debug APK share the local debug signing identity. Both use distinct package IDs and therefore cannot replace each other.

## Not verified on hardware

- Current E2003 runs Android 4.4.4/API 19. A newer Android version/emulator was not available, so newer-version behavior is not claimed.
- Multiple Kodi instances, failed/auth-rejected endpoints, Zeroconf disabled/no-result behavior and discovery interrupted by a lifecycle transition were not physically simulated. The active Kodi instance proved DNS-SD discovery and authenticated JSON-RPC verification.
- D-pad, transport, volume, audio/subtitle changes, seek, physical sensor rotation and Wi-Fi interruption were not re-issued after this build because those actions affect active Kodi playback/state. Their protected code is unchanged from v0.2; earlier physical verification is recorded above in the v0.3 report and by the user.
- Automatic Gradle unit tests have no source files and therefore report `NO-SOURCE`. Android runtime checks were manual ADB checks on the E2003.
- The build uses JDK 21 while targeting Java 8 source/bytecode; Gradle emits the JDK deprecation warning. Build and API 19 compilation succeed.

## APK artifacts

- `dist/FarfarRemote-App-v0.4.0.apk` — ordinary app, `org.farfarremote.app`.
- `dist/FarfarRemote-OS-v0.4.0.apk` — HOME launcher, `org.farfarremote`.
- SHA-256 values are in `dist/SHA256SUMS-0.4.0.txt`.
