# FarfarRemote OS — build and test report

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
