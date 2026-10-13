# FarfarRemote 0.2.0 — build and test report

**Target:** Sony Xperia E4g E2003, Android 4.4.4/API 19, firmware 25.0.A.2.31, 540×960 at 240 dpi. **No root, bootloader, system image or package debloat was performed.**

## Automated and local checks

- `ANDROID_HOME=/tmp/farfar-sdk ANDROID_SDK_ROOT=/tmp/farfar-sdk ./gradlew assembleDebug` — **PASS**. The temporary SDK had Platform 34 and Build Tools 34.0.0. Java 8 source/target deprecation warnings are from the JDK 21 build runtime; compilation succeeded.
- `aapt dump badging app/build/outputs/apk/debug/app-debug.apk` — **PASS**: package `org.farfarremote`, versionCode 2/versionName 0.2.0, min SDK 19, target SDK 28; HOME launcher activity and INTERNET/ACCESS_NETWORK_STATE/VIBRATE permissions present.
- No third-party Gradle dependencies and no Google Play Services integration.
- PNG sources were inspected for RGBA/alpha and dimensions. The three sheets were split to five/four/four separate buttons; original PNGs are preserved in `graphics/originals/` and `FarfarRemote_Asset_Pack/`.
- The deliverable APK is **1,103,128 bytes (about 1.05 MiB)**. Its SHA-256 matches the Gradle output APK.

## Physical Xperia checks

ADB confirmed the connected target as Sony E2003, build `25.0.A.2.31`, API 19. The device serial is omitted from this report.

- Installed app before test: 0.1.0/versionCode 1. Ran `adb install -r dist/FarfarRemote-0.2.0-api19-debug.apk` — **PASS**, update succeeded in place. It retained the same package and signing identity.
- Shared-preferences file SHA-256 immediately before and after that update was identical (`47138767cd81ec7b03ed8de44ec868017035e26eb0f4442d5b78352457d33c47`). No preference values were printed. Later orientation testing changed only the saved orientation key and left Portrait selected.
- Launched `org.farfarremote/.MainActivity` — **PASS**: activity remained resumed and no fatal app exception appeared in the captured logcat window.
- Opened Settings using the screen, selected Landscape, confirmed Android reported landscape configuration; selected Portrait, confirmed portrait configuration and saved `orientation=portrait`. Selected Auto and confirmed it saved; the device stayed in portrait while tested. Sensor-driven rotation after physically turning the handset remains a manual check.
- Pressed the on-screen Settings control again after rotating and used the Settings UI — **PASS**.
- Opened Android Wi-Fi Settings from FarfarRemote Settings and returned using Back — **PASS**. This gives network credential entry a fallback path when Kodi is offline.
- Settings “Test connection” to the saved Kodi endpoint — **PASS**; response reported connected. This exercises the actual phone-to-Kodi JSON-RPC path (`JSONRPC.Ping` and `Application.GetProperties`). No playback-changing Kodi command was issued during the test.
- Current FarfarRemote process measurement after returning to the remote: **18,100 kB PSS**, **61,960 kB RSS**, **26 threads**, one `top` sample at **0% CPU**. This is a single warm-idle snapshot, not an average or an improvement comparison. The 0.1 baseline for this device/app was not captured in this run.

## Still requires manual verification

- Rotate the physical phone with Auto selected and verify both layouts in normal use.
- Test D-pad directions/OK, each transport/navigation/category touch target and key/HID input against Kodi. ADB touchscreen taps confirmed UI interaction, but the whole remote map was not exercised.
- Play a video with multiple audio and subtitle streams; verify metadata, alternative names, selected flags, Off, poster, episode fields and seek. Current Kodi test verified connection only, not media switching.
- Verify progress polling/seek support on the active player, mute/volume behavior and reconnection after a real Wi-Fi/Kodi outage.
- Verify Bluetooth, charging/wake, sustained memory/CPU and cold boot. No device reboot or charger/Bluetooth regression was run.
- Test offline Settings by disabling Kodi or joining a network with no Kodi host. The code keeps Settings local and handles timeout/auth/address failures, but this was not simulated on the phone.
- Splash uses a first-render overlay with no fixed sleep. Its exact visible duration and appearance need visual check on device; screenshot export was unavailable in this ADB session.

## Debloat gate

Do not debloat yet based only on this app test. First use 0.2 as the selected HOME remote, confirm Wi-Fi text input/recovery and ADB APK install, then take a steady-state baseline. The recommended first system trial is **Phase A only**, and only after FarfarRemote stability verification. Its first default five-package batch is:

1. `app.gpsme` — GPSME navigation app
2. `com.facebook.katana` — Facebook
3. `com.mobisystems.office` — Office editor
4. `com.navigon.navigator_select_sony_eu` — NAVIGON
5. `com.scee.psxandroid` — PlayStation companion app

Use the dry-run plan first and then explicit `--apply --approve-phase A`; follow the script's typed confirmation and complete every regression prompt. Reboot and compare active and cached PSS separately before the second A batch. A/B/C/D remain reversible per user 0; no root or `/system` changes.
