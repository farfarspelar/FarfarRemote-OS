# FarfarRemote OS 0.2

En dedikerad Kodi-fjärrkontroll för Xperia E4g E2003. Projektet bygger vidare på samma Android-app och behåller `org.farfarremote` samt inställningsfilen från 0.1. Ingen Play Services-integration eller extern appberoende har lagts till.

## Bygg och installera på Linux Mint

Krav: JDK 17+, Android SDK Platform 34 och Build Tools 34.0.0. Gradle Wrapper använder Gradle 8.7.

```sh
./gradlew assembleDebug
./tools/install_farfarremote.sh dist/FarfarRemote-0.2.0-api19-debug.apk
```

APK: [FarfarRemote-0.2.0-api19-debug.apk](dist/FarfarRemote-0.2.0-api19-debug.apk), minSdk/API 19, versionCode 2. Byggresultatet ligger även i `app/build/outputs/apk/debug/app-debug.apk`. Installationsskriptet kräver en enda auktoriserad ADB-enhet med E2003-identitet och kör `adb install -r`; det avinstallerar inte appen och rensar inte inställningar. Välj FarfarRemote som Android HOME när systemet frågar.

## Användning

Stående är standard. Kugghjulet öppnar Kodi Connection, Display, Remote och System Information även när Kodi är offline. 0.1-värdena (`host`, `port`, `user`, `pass`) återanvänds; de ersätts inte av exempeldata. Skärmläge och fjärrinställningar sparas separat.

På Kodi aktiveras fjärrstyrning via HTTP under Settings → Services → Control. Ange värd/IP, port (ofta 8080) och vid behov inloggning i Settings. Kontrollpanelen hämtar Now Playing och spårstatus asynkront. Touch D-pad-zonerna delar en bild men är åtskilda med en mittzon och fyra icke överlappande riktningssektorer.

Kodi-anropen följer JSON-RPC API v13.11 för `Player.GetProperties`, `Player.GetItem`, `Player.Seek`, `Player.GoTo`, `Player.SetAudioStream`, `Player.SetSubtitle`, `Input.*`, `GUI.ActivateWindow` och `Application.*`: [Kodi JSON-RPC API v13.11](https://kodi.wiki/view/JSON-RPC_API/v13.11). Äldre Kodi-versioner kan exponera en annan API-schema; kontrollera den aktiva serverns API-svar.

## Grafik

Originalfilerna finns kvar i `FarfarRemote_Asset_Pack/` och kopian `graphics/originals/`. Android använder beskurna, nedskalade resurser i `app/src/main/res/drawable-nodpi/`. Mockuper och den statusknapp som har fast texten “Kodi · MeLE / Connected” packas inte in som skärmbakgrund eller statusindikator. Se [graphics/README.md](graphics/README.md).

## Tester och systemrensning

Bygg- och enhetstester redovisas i [TEST_REPORT.md](TEST_REPORT.md). Ändringar i systempaket, root, bootloader eller bootanimation ingår inte. Debloat-verktygen behåller dry-run som standard. Efter att 0.2 har använts stabilt och baseline-mätningen tagits rekommenderas endast **fas A, första batchen om fem paket** enligt [debloatplanen](reports/debloat/DEBLOAT_0.1_PLAN.md) och [paketlistan](tools/debloat_packages.tsv); kör hela regressionslistan innan nästa batch.

Fas A påverkar inte `org.farfarremote`, Android Settings/SettingsProvider, tangentbord, input devices, Wi-Fi/system connectivity, `com.android.shell` (ADB), PackageInstaller, Android/MediaTek Bluetooth eller strömhantering. De är inte A-kandidater; centrala systempaket är dessutom markerade `NEVER`. Sony HOME bevaras som reservlauncher. Ingen faktisk debloat har körts.

```sh
./tools/debloat.sh --phase A                 # visa plan, ingen ändring
./tools/debloat.sh --measure baseline        # mätning via ADB
./tools/debloat.sh --phase A --apply --approve-phase A
```

Appen kan återställas genom att välja Android Settings → Apps → FarfarRemote → Clear defaults eller välja en annan HOME-app. Behåll Sony HOME och ADB under utveckling.
