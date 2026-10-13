# FarfarRemote OS – målarkitektur

## Beslutsförslag

Börja med **alternativ A: avskalad originalfirmware** och gör FarfarRemote till enda hemaktivitet. Det använder Sonys fungerande MT6732-kärna, display-, touch-, Wi-Fi- och strömhantering. Det ger en kontrollerbar väg till en användbar prototyp utan att först porta en hel äldre Androidplattform. Bygg alternativ B först när A har mätts och en tydlig begränsning kräver det.

E2003 rapporteras med Android 4.4.4/API 19 och bootloadern uppges tillåta upplåsning. Dessa uppgifter är användarens inventering, inte självständigt avlästa från enheten i denna arbetsfas.

FarfarRemote 0.1 finns nu som Java/Android-projekt i `app/`: ingen extern runtime dependency, HOME-intent, fullscreen touchkontroller, Kodi JSON-RPC och statusping/återanslutning. APK:n har kompilerats med minSdk 19; fysisk UI- och Kodi-testning återstår.

## Lager

1. **Bootkedja och leverantörskärna**: behåll Sony/MediaTek bootkedja, kärna och proprietära HAL-/firmwaredelar tills en exakt kompatibel ersättare har byggts och verifierats.
2. **Android 4.4.4-plattform**: behåll SurfaceFlinger, system_server, Package Manager, Wi-Fi-stack, input, ljud och de gränssnitt som E2003:s HAL kräver. Avinstallera inte paket i blindo.
3. **FarfarRemote-app**: en enda landscape/portrait-anpassad kioskapp efter behov; HOME-intent som standardlauncher, immersive mode, lokal UI, Kodi-klient och återanslutningslogik. Android 4.4 kan dölja systemfälten med immersive sticky, men en vanlig app kan inte garantera att systemdialoger/överlapp försvinner.
4. **Fysisk kontroll**: mappa Android KeyEvent-koder till abstrakta handlingar; senare USB/Bluetooth-HID eller en kontrollerbrygga ska använda samma handlingar.
5. **Drift/återställning**: USB debugging endast i utvecklingsläge, versionshanterade konfigurationer, fullständig originalfirmware med verifierad återställningsväg före systemändringar.

## Uppstart och drift

Målbilden är boot → Androids nödvändiga tjänster → FarfarRemote som HOME → Wi-Fi färdig → Kodi hittad/ansluten. Appen ska vara idempotent vid processdöd/omstart, visa lokal status utan nät, och återansluta med exponentiell backoff och jitter. Wi-Fi-anslutning bör först konfigureras i Androids ordinarie inställningar; senare kan en låst konfiguration automatiseras. Håll skärmen vaken vid dockad drift och välj kontrollerad laddningspolicy efter batteri- och värmetest.

## Icke-mål och gränser

Detta är fortsatt Android, inte ett fristående Linux-system. AOSP-bygge kräver modellens board/device-konfiguration, rätt 3.10-generationens vendor kernel, proprietära blobs och matchande verktygskedja. Ingen exakt E2003-port eller reproducerbar buildmiljö har ännu verifierats. Att modernisera Android utan komplett MTK-stöd är inte ett rimligt första steg.

## Mätetal

Registrera kallstart till första interaktion, kallstart till Wi-Fi, RAM/PSS för toppprocesser, idle-RAM, appens första bildruta, Wi-Fi-återhämtning efter AP-bortfall och stabilitet efter 24 h. Samma laddningsläge, temperatur, nät och mätmetod används i före/efter-jämförelser. Baslinjemätning saknas tills fysisk ADB-åtkomst fungerar.

## Källor och evidens

- Sony bekräftar upplåsning som modell-/statusberoende; unlock kräver kod och fastboot, och upplåsning i sig ger inte root: [Sony bootloader guide](https://developerworld.wpp.developer.sony.com/open-source/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader).
- Enhetsmodellens Android/API/hårdvaruprofil i användarens uppgifter behöver verifieras direkt mot enheten.
- Community-svar uppger ingen officiell LineageOS-build för E4g och att senaste tillgängliga Android var KitKat: [/e/OS community](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466). Detta är sekundär community-evidens, inte bevis att ingen fungerande privat port finns.
