# Firmwarestrategi

## Rekommendation: A först

Behåll den exakta 25.0.A.2.31-installationen och gör en kiosk/launcher-app. Ta först bort eller inaktivera en komponent endast efter inventering och helst med reversibel paketåtgärd. Factory-image ska arkiveras lokalt, dess ursprung och hash dokumenteras och återflashvägen provplaneras. Sony-bootloadern tillåter enligt uppgift upplåsning, men detta måste verifieras i service-menyn och unlock kräver en modellspecifik kod. Upplåsning är inte root och kan radera data/ändra DRM-relaterade funktioner.

**Varför:** fungerande radio, skärm, touch, Wi-Fi och energihantering är viktigare än en teoretiskt renare userspace. Det finns ingen bekräftad officiell LineageOS-build för E2003; communityuppgift säger att Android 4.4.4 var sista versionen. En modern AOSP-port kräver enhetskonfiguration, vendor blobs, kompatibel kernel och omfattande tester. Den kan inte rekommenderas som första praktiska väg.

## Alternativ B – villkorad undersökning

Om originalsystemet inte kan hållas stabilt efter reversibel rensning, inventera källkod för exakt kernel-board, device tree, proprietary blobs, boot image-format, recovery och partitioner. Bygg först en reproducerbar, signerad/återställningsbar image utan att flasha. Boot-test/flash kräver separat uttryckligt godkännande och en modellverifierad återställningsplan. Använd inte E2033 dual-SIM, E1 eller annan MT6732-image som substitut.

## Root och återställning – exakt firmware

En historisk 4PDA-tråd har användarrapporter som uttryckligen nämner **E2003 25.0.A.2.31** och KingRoot; andra inlägg nämner varierande framgång och försök att byta KingRoot/SuperSU. Det verifierar endast att enskilda användare hävdade resultat år 2016. Tråden tillhandahåller här inget auditerat exploit, hashverifierad root-binär, reproducerbart steg-för-steg-flöde eller test på vår firmwarevariant. Därför är ingen rootmetod tekniskt verifierad eller säker nog att rekommendera/köra. Undvik KingRoot/KingoRoot-appar eller PC-verktyg från okända speglar: de är slutna, gamla och får privilegierad åtkomst.

Sonys officiella bootloaderupplåsning är en verifierad generell Sony-process men är **inte root** och gör inte i sig systempartitionen skrivbar. Ägaren uppger att bootloadern är upplåst. En icke-skrivande Fastboot-kontroll bekräftade produkt E2003 och rätt bootloader-/firmwareversion, men `fastboot getvar unlocked` returnerade ett tomt värde och `fastboot oem device-info` svarade `unknown command`; upplåsningen kunde därmed inte verifieras oberoende via dessa gränssnitt. Den efterföljande ADB-sessionen gav fortsatt `uid=2000(shell)` och `su` hittades inte i de kontrollerade standardvägarna. En upplåst bootloader innebär alltså inte att nuvarande Android-session har root. Det finns inget i underlaget som verifierar E2003-kompatibel TWRP/custom recovery eller en signerad rootad boot image för just 25.0.A.2.31. Alltså ingen fastboot-image får väljas utifrån E2033, E2105 eller annan modell.

### Möjligt utan root (första prototypen)

- Installera FarfarRemote som vanlig APK och välja den som HOME-app.
- Dölja Androids status-/navigationsfält medan appen är i förgrunden med KitKats immersive sticky-läge; systemdialoger och vissa systemöverlägg kan fortfarande visas.
- Hålla skärmen vaken, lagra Kodi-inställningar, Wi-Fi konfigureras via Android UI, automatisk klientåteranslutning.
- Samla auditdata via ADB och kontrollera applikations-/tjänstedumpen. Vissa filer/loggar är skyddade utan root.
- Inaktivera vissa appar via Inställningar om firmware tillåter det; gör bara manuellt efter paketgranskning och håll launcher/recovery tillgänglig.

### Reversibel Phase A på E2003: verifierad begränsning (2026-10-14)

En skrivskyddad kontroll på den anslutna E2003/API 19 visade att alla fem tidigare godkända Phase A-paket fortfarande är aktiverade. ADB-kommandot `pm disable-user --user 0 app.gpsme` hade tidigare avvisats av firmware med `SecurityException` innan något paket ändrades. Med telefonen upplåst öppnades Androids Appinfo för `app.gpsme` (visningsnamn KidsControl): skärmen erbjöd **Tvinga avslut** och **Avinstallera**, men ingen **Inaktivera**-knapp. Ingen knapp trycktes och FarfarRemote återfördes till förgrunden.

Slutsats: Phase A kan inte genomföras med den planerade reversibla inaktiveringen på den här firmwareversionen via ADB eller Appinfo-vyn. Avinstallation är en annan, mer destruktiv åtgärd och får inte ersätta inaktivering utan separat godkännande och verifierad återställningsväg. Ingen paketändring, root eller flashning har gjorts. Ägaren uppger att bootloadern redan är upplåst; inget upplåsningskommando kördes i denna arbetsfas.

Sony Open Devices dokumenterar att bootloaderupplåsning **inte ger root**, utlöser fabriksåterställning och inte kan återställas till låst bootloader eller ursprungliga DRM-nycklar. Det gör upplåsning till en separat riskfråga, inte en lösning på `pm disable-user`-begränsningen. Se [Sonys aktuella upplåsningsguide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader/). En forumrapport från 2016 säger att KingRoot fungerade på E2003 med 25.0.A.2.31, men den identifierar inte en auditerad binär/hash eller reproducerbar exploateringskedja. Det är ett historiskt påstående, inte en verifierad metod; KingRoot/KingoRoot rekommenderas inte.

### Kräver root eller modifierad firmware

- Ta bort/korruptionssäkert ersätta systempaket från `/system`, init.rc/systemtjänster och bootanimationsfiler.
- Göra FarfarRemote till priv-app/systemapp, ta bort systemets status-/navigeringspolicys eller blockera systemdialoger helt.
- Ändra boot image, kernel, SELinux-/init-policy eller startordning.
- Bygga ett verkligt minimalt OS/systemimage. Det kräver modellmatchad board-konfiguration, kernel och vendor blobs; ingen komplett byggkedja för E2003 är ännu verifierad.

Root via en gammal exploit kan också innebära systemskrivning och bootloop-risk. Innan något sådant övervägs behövs hashverifierad exakt regional firmware, fungerande Flashtool/återställning för just E2003, kopia och identifiering av partitioner samt separat uttryckligt godkännande. ADB/Fastboot-skrivkommandon ingår inte i leveransen.

Före eventuell upplåsning krävs:

1. Bevisa fysisk USB/fastboot-kommunikation och exakt produktkod.
2. Hämta Sony-upplåsningsinstruktion/kod med rätt IMEI och kontrollera unlock status på enheten.
3. Hämta exakt E2003 firmware från trovärdig källa, kontrollera hash/signatur där det finns, och bekräfta att återställningsverktyget fungerar med aktuell Linuxmiljö.
4. Säkerhetskopiera relevanta partitionsmetadata och personliga data om något oväntat finns; bevara radio-/kalibreringspartitioner.
5. Få separat godkännande innan unlock eller skrivning till enheten.

## Licens och proveniens

Återanvändning av öppna kernelkällor måste följa licensvillkor; Sonys/MediaTeks proprietära blobs och firmware har separata distributionsvillkor. För ett privat bygge kan lokalt extraherade blobs vara tekniskt nödvändiga men deras redistribution ska inte antas vara tillåten. Varje artefakt ska dokumentera källa, modell, region, version och SHA-256.

## Källor

- [Sony: upplåsning av bootloader](https://developerworld.wpp.developer.sony.com/open-source/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader)
- [4PDA E4g-firmwaretråd](https://4pda.to/forum/index.php?showtopic=668811&st=320), historiska användarrapporter om KingRoot på E2003 25.0.A.2.31; ej säkerhetsverifiering eller endorsement.
- [Sony Support: E2003/E2006/E2053 användarhandbok](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf)
- [Firmwarelista från tredjepart](https://androidfilehost.com/?flid=212192&w=files) listar E2003 25.0.A.2.31-varianter, men verifierar inte filintegritet eller återställbarhet.
- [Communityuppgift om E4g-ROM-stöd](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466), informativ men inte auktoritativ.
