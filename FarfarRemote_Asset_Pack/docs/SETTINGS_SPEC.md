# FarfarRemote Settings Spec

## Mål
Inställningar ska flyttas bort från huvudskärmen och ligga i ett separat Settings-läge.

Huvudvyn ska vara ren, snabb och fokuserad på fjärrkontrollen.

## Settings ska innehålla

### Kodi / Network
- Host / IP-adress
- Port
- Username
- Password
- Visa/dölj lösenord
- Test connection
- Save settings
- Feedback om anslutning lyckades eller misslyckades

## Orientation / Display
- Portrait
- Landscape
- Auto

Valet ska sparas och återställas efter omstart.

## Remote behavior
- Auto reconnect on/off
- Haptic feedback on/off
- Keep screen awake on/off
- Future placeholder för Bluetooth / hardware buttons

## Viktigt
Settings ska kunna öppnas även när Kodi är offline.
Man ska alltså kunna ändra nätverksinställningar även om uppkopplingen är nere.

## UX-princip
- Enkel
- Tydlig
- Inga tekniska internfel på startsidan
- Begripliga felmeddelanden

## Språkval
Visa alltid tillgängliga Kodi-spår dynamiskt. Knapparna är språkneutrala, och alla faktiska språkval hämtas via JSON-RPC.
