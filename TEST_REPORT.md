# FarfarRemote 0.4.2 RC1 — release track split QA

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

- `dist/FarfarRemote-App-v0.4.2-rc1.apk` — target API 36, min API 19.
- `dist/FarfarRemote-OS-v0.4.2-rc1.apk` — target API 28, min API 19.
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
