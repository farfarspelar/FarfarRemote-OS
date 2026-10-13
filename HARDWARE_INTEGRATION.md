# Hårdvaruintegration

## Nuvarande enhet

E2003:s rapporterade MT6732-plattform, 540×960-touchskärm och Wi-Fi är primära gränssnitt. Alla egenskaper och pinnivåer måste bekräftas för just E2003. Använd inte pinout eller batteridata från E2033/E2006 utan jämförelse.

## Knappar och framtida kontroller

Appen ska ha ett logiskt handlingslager: `UP`, `DOWN`, `LEFT`, `RIGHT`, `SELECT`, `BACK`, `PLAY_PAUSE`, `STOP`, `VOLUME_UP`, `VOLUME_DOWN` samt konfigurerbara `FUNCTION_n`. Mappa först befintliga volym-/powerknappar med Android KeyEvent och mät key repeat/long press. Powerknappen bör behålla systemets säkra funktion.

För externa kontroller prioriteras standard HID-enhet via Bluetooth eller USB OTG, om Android 4.4-kernel, drivrutin, USB-hostläge och strömförsörjning verifieras. USB-mikrokontroller kan presentera sig som HID-tangentbord och därmed undvika egen kernel-drivrutin. Serial/CDC-brygga kräver USB-hostadapter, rätt tillbehörsström och applikationsstöd; kontrollera SELinux/USB-access i aktuell build. Trådlös mikrokontroller behöver parnings-/återanslutningstest och fysisk fallback.

## Bluetooth

Behåll Bluetooth-stack/firmware bara om verklig användning mot tänkt kontroll är bekräftad. Mät standbyförbrukning och återanslutning. Om inga Bluetooth-tillbehör behövs, inaktivera radio i drift utan att ta bort frameworkpaket innan beroenden är inventerade. BLE-protokollstöd ska inte antas för KitKat-device stack utan test.

## Schassi och docka

Schassit ska lämna åtkomst till power/volym och USB, samt ha öppningar för högtalare och ventilation. Utforma knappar så att de inte hålls intryckta av misstag. Dockan ska ge stabil USB-laddning med mekanisk avlastning; mät laddning och temperatur på den aktuella enheten innan kontinuerlig drift.

Konstruktionen måste hålla touchyta fri, skydda batteriet från tryck/värme, avlasta USB-kontakten och göra reset/USB-debugging åtkomligt under service. Ingen laddningsmodifiering eller öppning av batteripaket rekommenderas.

## Testmatris

- Knappar: kort/lång press, samtidig input, repeat och app i förgrund/bakgrund.
- USB: OTG/HID enumeration, strömbudget och återanslutning efter dockning.
- Bluetooth: pairing, sleep/wake, radiobortfall, batteriförbrukning.
- Docka: uppstart vid ansluten ström, återstart efter strömavbrott, batteritemperatur.
- Nätverk: accesspunkt av/på, svag signal, DHCP-omförhandling, Kodi omstart.
