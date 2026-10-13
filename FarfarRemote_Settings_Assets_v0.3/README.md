# FarfarRemote Settings Asset Pack v0.3

För Android 4.4.4/API 19. Detta är en **resursleverans**, inte en installerbar APK.

## Innehåll
- `assets/settings/backgrounds`: porträtt-/landskapsbakgrunder samt kort- och panelgrafik.
- `assets/settings/fields`: tomma, transparenta inputfält (normal och fokus).
- `assets/settings/buttons`: visuella bakgrundsknappar, inklusive `button_coffee_discreet.png`.
- `assets/settings/toggles`: växelspår och separata on/off-handtag.
- `assets/settings/icons`: separata transparenta ikoner, inklusive `ic_coffee.png`.
- `assets/settings/reference`: AI-genererad inspirationsbild. Den är inte avsedd att användas som en hel skärmbild.

## Mycket viktigt
Alla knappbakgrunder saknar fast text. Android TextView ska lägga på rubriker, anslutningsvärden och statustext dynamiskt. Till skillnad från ett genererat knappsheets ligger varje komponent i en egen PNG och har riktig alfatransparens.

För minnesbegränsad Xperia E2003: skala och optimera resursbilder utifrån faktiska dp-mått; överväg XML shape drawables eller 9-patch för töjbara bakgrunder. PNG-filerna är visuella utgångspunkter.

## Buy Me a Coffee
- `button_coffee_discreet.png` är en diskret mörk sekundär knappbakgrund. Lägg `ic_coffee.png` till vänster och dynamisk text `Buy Me a Coffee` ovanpå.
- Placera i slutet av Settings/About, efter Systeminformation. Den ska aldrig störa Kodi-funktionerna.
- Knappen öppnar endast användarens **verifierade egna Buy Me a Coffee-URL** i en extern webbläsare. Ingen donationstjänst är integrerad och inget URL är förinställt.
- Om URL saknas: dölj knappen eller visa den inaktiv. Låt Codex inte gissa kontonamn eller länkar.
- Visa ingen annonsruta, påminnelse eller återkommande popup.
- Använd egen kaffekoppsikon i stället för att låtsas att detta är en officiell märkeslogotyp. Kontrollera tredjepartsvarumärkesregler om officiell branding önskas senare.

## Integrationsråd
1. Läs befintliga Settings-koden och bevara sparade host/port/user/pass och orienteringsvärden.
2. Använd `bg_portrait.png`/`bg_landscape.png` som bakgrund; bygg verkliga klickbara Android Views ovanpå.
3. Anpassa storlek efter 540x960 och 240 dpi. Undvik skarpt blått på allt.
4. Ingen root, debloat, bootanimation eller systemmodifiering krävs.
5. Respektera GPL-3.0-licens och dokumentera grafikens ursprung separat.
