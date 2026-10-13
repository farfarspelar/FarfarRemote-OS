# FarfarRemote OS 0.3.0

En dedikerad Kodi-fjärrkontroll för Xperia E4g E2003. Projektet behåller Android-paketet `org.farfarremote`, HOME-launcher-intentet och inställningsfilen från 0.1/0.2. Version 0.3 fokuserar på Settings-designen och ändrar inte Kodi-klienten eller fjärrkontrollens funktionslager. Ingen Play Services-integration eller extern applikationsberoende har lagts till.

## Bygg och installera på Linux Mint

Krav: JDK 17+, Android SDK Platform 34 och Build Tools 34.0.0. Gradle Wrapper använder Gradle 8.7.

```sh
./gradlew assembleDebug
./tools/install_farfarremote.sh dist/FarfarRemote-0.3.0-api19-debug.apk
```

APK: [FarfarRemote-0.3.0-api19-debug.apk](dist/FarfarRemote-0.3.0-api19-debug.apk), minSdk/API 19, versionCode 3. Byggresultatet ligger även i `app/build/outputs/apk/debug/app-debug.apk`. Installationsskriptet kräver en enda auktoriserad ADB-enhet med E2003-identitet och kör `adb install -r`; det avinstallerar inte appen och rensar inte inställningar. Välj FarfarRemote som Android HOME när systemet frågar.

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
