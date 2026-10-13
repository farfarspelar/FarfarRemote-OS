# CODEX – FarfarRemote v0.2

Vi har nu en fungerande FarfarRemote 0.1 på riktig hårdvara:
Sony Xperia E4g E2003, Android 4.4.4, API 19.

Appen fungerar som launcher och kan redan styra Kodi.
Nu ska du bygga nästa version med förbättrad design och bättre struktur.

## Viktigt
Detta uppdrag gäller appen/UI:n.
Rör inte systempartitioner, root, bootloader eller debloat i detta uppdrag.

## Hårdvara / målplattform
- Sony Xperia E4g E2003
- Android 4.4.4
- API 19
- 540x960
- 240 dpi
- Home/launcher-läge används

## Referenser
Använd dessa filer som designreferenser:
- assets/mockups/farfarremote_portrait_reference.png
- assets/mockups/farfarremote_landscape_reference.png

Kopiera inte mockuperna pixel-exakt.
Använd dem som riktning för layout, färgkänsla, struktur och UX.

Läs även:
- docs/UI_SPEC_v0.2.md
- docs/SETTINGS_SPEC.md
- docs/DESIGN_NOTES.md
- docs/IMPLEMENTATION_CHECKLIST.md

## Huvudmål
Bygg FarfarRemote v0.2 med:
1. Ny portrait-layout som standard
2. Separat settings-vy
3. Stöd för landscape-layout
4. Tydlig now playing-panel
5. Stöd för subtitles och audio language
6. Bättre visuell design

## Funktioner som ska prioriteras

### Main / Remote screen
- mörkt premium-gränssnitt
- stor, tydlig D-pad / OK
- Back
- Home
- Play/Pause
- Stop
- Volym upp/ned
- ev. previous/next/rewind/fast forward
- anslutningsstatus
- kodi-hostnamn/enhetsnamn

### Now Playing
Visa:
- titel
- episod / undertitel när relevant
- elapsed time
- total time
- progress bar
- playing/paused
- poster/thumbnail om tillgängligt
- audio language
- subtitles language

### Audio / Subs
Det ska finnas två tydliga actions:
- Audio
- Subs

Användaren ska kunna välja stream/spår från Kodi.
Anime-usecase är viktigt:
- japanskt ljud
- engelsk text

### Settings
Separat settingsskärm med:
- host/IP
- port
- username
- password
- visa/dölj lösenord
- test connection
- save settings
- orientation: portrait / landscape / auto
- auto reconnect
- keep screen awake
- haptic feedback (endast om faktiskt fungerande)

## Arkitektur
Separera tydligt:
- UI
- settings storage
- kodi connection layer
- player state
- audio/subtitle actions
- portrait layout
- landscape layout

Förbered gärna en intern action layer så att framtida fysiska knappar kan återanvända samma kommandon.

## Androidkrav
- Min SDK: 19
- Inga onödiga beroenden
- Ingen Google Play Services
- Låg RAM- och CPU-belastning
- Fungerar fortsatt som HOME-app

## Testkrav
Verifiera:
- Portrait som standard
- Landscape fungerar
- Auto mode fungerar
- Settings kan öppnas utan Kodi-anslutning
- Sparade settings överlever appomstart
- Kodi-kontroller fungerar fortsatt
- Audio stream kan bytas
- Subtitle stream kan bytas
- Appen känns bättre visuellt än 0.1

## Leverans
Jag vill ha:
- uppdaterad källkod
- körbar APK
- kort changelog
- eventuella kända begränsningar
- installationsinstruktioner

Prioritera:
1. fungerande UX
2. snyggare design
3. tydligare struktur
4. faktisk nytta

## Grafiska produktionsassets och uppstartslogo
Använd `assets/ui/` för de faktiska PNG-kontrollerna. Alla bilder har alfa; separera de sammanfogade knappsheets till individuella knappar och ge varje knapp en egen touchyta och tillgänglighetsetikett. Behåll bildproportioner och minimera GPU-/RAM-belastning på Android 4.4.4.

Använd `assets/ui/button_audio_selector.png` och `assets/ui/button_subs_selector.png` i stället för tidigare hårdkodade språkvarianter. De visar bara Audio respektive Subtitles. Lägg aktuellt språk eller spårnamn i dynamiska Android TextViews baserat på faktiskt Kodi-svar (inklusive Okänd/Av om relevant).

Vid appstart visa `assets/branding/farfarremote_os_boot_logo.png` på en kort, responsiv splash-skärm. Blockera inte appstart i väntan på Kodi. Ändra INTE bootloader, bootanimation eller systempartitioner i denna UI-fas.
