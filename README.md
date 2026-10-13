# FarfarRemote 0.4.0

FarfarRemote controls Kodi over its HTTP JSON-RPC interface. It now ships in two Android variants built from the same source and sharing the Kodi client, remote controls, Settings, graphics and preferences logic.

**FarfarRemote App**

For everyday Android phones. Install the APK and use it like any other app. No root or system modification is required. It has a normal app icon, does not claim the Android HOME role, and keeps Android's ordinary navigation. Its separate package ID (`org.farfarremote.app`) allows it to coexist with FarfarRemote OS.

**FarfarRemote OS**

For dedicated remote-control devices. Uses FarfarRemote as the Android HOME launcher and retains the established package ID (`org.farfarremote`) for in-place updates on the Xperia E2003. Android system optimization is optional and is a separate advanced procedure; this release does not root, flash or debloat a device.

Both variants require Android 4.4/API 19 or newer and include the existing Kodi controls, Audio/Subtitles selection, orientation modes, Settings and Buy Me a Coffee link. No Google Play Services or tracking SDK is used.

## Build and install

Build both debug APKs on Linux Mint with JDK 17+, Android SDK Platform 34 and Build Tools 34.0.0 (Gradle Wrapper 8.7):

```sh
ANDROID_HOME="$HOME/Android/Sdk" ./tools/build_distributions.sh
```

The script runs available Gradle unit-test tasks, assembles both flavors, verifies package/version IDs, and writes SHA-256 checksums. Artifacts are `dist/FarfarRemote-App-v0.4.0.apk` and `dist/FarfarRemote-OS-v0.4.0.apk`. These are debug-signed builds. OS updates require the same signing key used for the installed build; the repository's current debug key matches the v0.3 APK used in development.

Install the ordinary app with `./tools/install_app.sh`. To update the dedicated E2003 installation, use `ANDROID_HOME=... ./tools/install_farfarremote.sh`; this script checks that the APK is the OS package, confirms E2003 identity and uses `adb install -r` without clearing app data. Never give the App APK to the OS installer; the package check rejects it.

## Kodi discovery

Settings retains the manual host, port, username and password fields. **Find My Kodi** searches only when tapped, using Android Network Service Discovery for Kodi's HTTP JSON-RPC DNS-SD service (`_xbmc-jsonrpc-h._tcp.`). A discovered endpoint is tested through Kodi JSON-RPC with the credentials currently in the visible fields. Only after the user chooses **Use and Save** are its host and port written; failed tests and canceled discovery leave existing settings intact. Kodi must announce services through Zeroconf and have HTTP control enabled; manual IP entry remains available. Kodi documents service announcements in [Settings → Services → General](https://kodi.wiki/view/Settings/Services/General), HTTP JSON-RPC setup in its [remote-control guide](https://kodi.wiki/view/Smartphone/tablet_remotes), and the `_xbmc-jsonrpc-h._tcp` HTTP service in Kodi service logs/source examples. Android NSD manages discovery itself; FarfarRemote does not hold a permanent multicast lock or scan in the background.

## Previous v0.3 documentation

The established Settings graphics, inline settings structure and GPL-3.0 license are retained. See the later sections below for build history, Kodi setup, graphics origin, tests and the separate Debloat 0.1 plan.

## Användning

Stående är standard. Kugghjulet öppnar Kodi Connection, Display, Remote och System Information även när Kodi är offline. Inställningarna använder samma nycklar (`host`, `port`, `user`, `pass`, `orientation`, `keep_awake`, `auto_reconnect`, `haptics`) och ersätter dem inte med exempeldata. Fälten är scrollbara och Androids tangentbord fungerar i båda skärmlägena. Rotation medan Settings är öppet behåller samma vy och osparade fältvärden.

Settings har en frivillig knapp längst ner som öppnar [Buy Me a Coffee](https://buymeacoffee.com/farfarspelar) med Androids vanliga externa webbläsarintent. Om ingen webbläsare kan hantera länken kopieras adressen till urklipp och en kort status visas. Ingen betalning, tracking eller extern SDK finns i appen.

På Kodi aktiveras fjärrstyrning via HTTP under Settings → Services → Control. Ange värd/IP, port (ofta 8080) och vid behov inloggning i Settings. Kontrollpanelen hämtar Now Playing och spårstatus asynkront. Touch D-pad-zonerna delar en bild men är åtskilda med en mittzon och fyra icke överlappande riktningssektorer.

Kodi-anropen följer JSON-RPC API v13.11 för `Player.GetProperties`, `Player.GetItem`, `Player.Seek`, `Player.GoTo`, `Player.SetAudioStream`, `Player.SetSubtitle`, `Input.*`, `GUI.ActivateWindow` och `Application.*`: [Kodi JSON-RPC API v13.11](https://kodi.wiki/view/JSON-RPC_API/v13.11). Äldre Kodi-versioner kan exponera en annan API-schema; kontrollera den aktiva serverns API-svar.

## Grafik

v0.2-fjärrkontrollens originalfiler finns i `FarfarRemote_Asset_Pack/` och `graphics/originals/`. v0.3:s kanoniska Settings-källa är den uppackade mappen `FarfarRemote_Settings_Assets_v0.3/`; dess ZIP-dubblett är ignorerad av Git. Utvalda ikoner skalas till 64×64 och de separata Settings-resurserna ligger i `app/src/main/res/drawable-nodpi/`. Skärmbildsreferensen används inte i appen. Se [graphics/README.md](graphics/README.md) och [grafikursprung/licens](graphics/SETTINGS_ASSETS.md).

## Tester och systemrensning

Bygg- och enhetstester redovisas i [TEST_REPORT.md](TEST_REPORT.md). Kör även `python3 tools/test_v03_contract.py` från en fullständig Git-checkout; det jämför kritiska fjärrkontrollmetoder med v0.2-baslinjen. Ändringar i systempaket, root, bootloader eller bootanimation ingår inte. Debloat-verktygen behåller dry-run som standard. Efter att fjärrkontrollen använts stabilt och baseline-mätningen tagits rekommenderas endast **fas A, första batchen om fem paket** enligt [debloatplanen](reports/debloat/DEBLOAT_0.1_PLAN.md) och [paketlistan](tools/debloat_packages.tsv); kör hela regressionslistan innan nästa batch.

Fas A påverkar inte `org.farfarremote`, Android Settings/SettingsProvider, tangentbord, input devices, Wi-Fi/system connectivity, `com.android.shell` (ADB), PackageInstaller, Android/MediaTek Bluetooth eller strömhantering. De är inte A-kandidater; centrala systempaket är dessutom markerade `NEVER`. Sony HOME bevaras som reservlauncher. Ingen faktisk debloat har körts.

```sh
./tools/debloat.sh --phase A                 # visa plan, ingen ändring
./tools/debloat.sh --measure baseline        # mätning via ADB
./tools/debloat.sh --phase A --apply --approve-phase A
```

Appen kan återställas genom att välja Android Settings → Apps → FarfarRemote → Clear defaults eller välja en annan HOME-app. Behåll Sony HOME och ADB under utveckling.
