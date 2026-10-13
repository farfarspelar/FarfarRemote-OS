# FarfarRemote UI Spec v0.2

## Mål
FarfarRemote ska utvecklas från en fungerande teknisk prototyp till en snygg, tydlig och praktiskt användbar dedikerad Kodi-fjärrkontroll för Sony Xperia E4g E2003.

Appen ska fungera som launcher/HOME-app och kännas som en riktig fjärrkontroll, inte som en testapp.

## Övergripande designmål
- Mörkt tema
- Midnattsblå / mörk blåsvart bakgrund
- Diskreta glow-effekter i blått/cyan
- Rundade knappar
- Snyggare och mer premium känsla än nuvarande version
- Tydliga kontraster och stora touchytor
- Kodis funktioner i fokus
- Layout ska fungera bra på 540x960, 240 dpi, API 19

## Orientering
Tre lägen ska stödjas:
1. Portrait / stående
2. Landscape / liggande
3. Auto / kombinerat

### Standard
Portrait ska vara standardläge.

### Viktigt
Landscape ska inte bara vara roterad portrait-layout.
Båda lägena ska ha egna anpassade layouter.

## Huvudvy – måste innehålla
- Appnamn / FarfarRemote
- Anslutningsstatus
- Namn på Kodi-enhet / värd
- Info-ruta / "Now Playing"
- Omslagsbild / thumbnail
- Titel
- Avsnitt / undertitel när relevant
- Progress / hur långt filmen/avsnittet spelats
- Nuvarande tid + total tid
- Knapp för subtitles
- Knapp för audio language
- Tydlig huvudnavigation (upp/ner/vänster/höger/OK)
- Back
- Home (Kodi-home)
- Play/Pause
- Stop
- Volym upp / ner
- Gärna snabbknappar för föregående/nästa/snabbspolning

## Now Playing-rutan
Now Playing-panelen ska vara tydlig och användbar, inte bara kosmetisk.

Den ska helst visa:
- omslagsbild / poster / thumbnail
- titel
- avsnittsnamn eller episodnummer om relevant
- progress bar
- elapsed time
- total duration
- status (playing / paused / stopped)
- ljudspråk
- subtitles-språk

Exempel på användningsfall:
Anime ska enkelt kunna växlas till japanskt tal + engelsk text.
Det ska gå snabbt att ändra ljudspråk och subtitles direkt från fjärrkontrollen.

## Audio/Subtitles
Det ska finnas två tydliga knappar:
- Audio
- Subs

Dessa ska öppna enkel dialog / meny med tillgängliga val från Kodi.

Exempel:
- Audio: Japanese / English / Swedish
- Subs: Off / English / Swedish

## Designreferenser
Se filer i:
assets/mockups/

- farfarremote_portrait_reference.png
- farfarremote_landscape_reference.png

Dessa ska användas som stil- och layoutreferens, inte kopieras exakt pixel för pixel.

## Prioritet
1. Funktion
2. Tydlighet
3. Responsivitet
4. Snyggare visuell design
5. Extra funktioner

## Dynamiska språkknappar
Använd generiska bildassets `button_audio_selector.png` (Audio) och `button_subs_selector.png` (Subtitles). Språk eller aktuellt spår ska presenteras som dynamisk UI-text från Kodi, aldrig inbäddat i bildfil.

## Uppstart
Använd `assets/branding/farfarremote_os_boot_logo.png` i en kort app-splash vid start, utan onödig väntetid. Att byta Sony-bootlogo/bootanimation är ett separat systemprojekt.
