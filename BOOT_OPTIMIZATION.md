# Uppstartsoptimering

## Mät före ändring

Baslinje saknas eftersom arbetsmiljön inte ser USB-enheten. När anslutning fungerar: mät fem kallstarter från avstängd enhet till (a) första interaktion, (b) appens första bildruta, (c) Wi-Fi anslutet och (d) Kodi nåbar. Använd samma nät, batterinivå/laddning och temperatur. Logga boot reason, `sys.boot_completed`, `dumpsys`-tider, minne och relevanta logcat-rader. Skilj kallstart från varm omstart.

## Åtgärdsordning med låg risk

1. Ersätt HOME/launcher med FarfarRemote; behåll systemets återställningsbarhet och Settings åtkomligt under utveckling.
2. Sätt animation scales till 0 eller av i utvecklingskonfiguration; mät UI och uppstart separat.
3. Implementera appens snabbstart: liten processyta, inga nätverksanrop på UI-tråd, cachea lokala vyer, lazy-load av sekundära kontroller.
4. Konfigurera Wi-Fi automatiskt via ordinarie systeminställning och hantera DHCP/AP-återkomst i klienten.
5. Inventera boot services/processer och paketberoenden; inaktivera först valfria användarappar en åt gången. Jämför kallstart, minne, Wi-Fi, input, ljud och crash logs.
6. Endast efter root/modifierad image och återställningsplan: ändra init-/systemtjänster eller ta bort systempaket. Behåll input, keystore, Wi-Fi, wpa_supplicant, dhcp, netd, SurfaceFlinger, mediaserver/audio, Package Manager och kritiska Sony/MTK-tjänster tills beroenden är kartlagda.

## Kiosk, energi och återhämtning

Android 4.4 immersive sticky döljer status- och navigeringsfält för appen. Det är inte sama som appliance-grade kiosk eller garantier mot systemdialoger. HOME-intent gör appen standardlauncher men första installation, uppdatering och krasch kräver fortfarande återhämtning. Under utveckling håll USB-debugging tillgängligt. I drift, undvik unattended uppdateringar.

Vid nätbortfall behåll fungerande lokalt UI och återanslut asynkront med 1, 2, 4, 8… sekunders backoff, maxgräns och jitter. Överväg fast DHCP-reservation på routern för Kodi-värd; använd mDNS endast efter test av Android 4.4/routern. Undvik polling med hög frekvens. Laddningsdocka: testa batteritemperatur, kontinuerlig laddning, skärmens timeout och wake locks. Håll skärmen tänd bara när användningen kräver det.

## Framgångskriterier

Efter varje ändring redovisa median och spridning för uppstartsmätningar, idle-/peak-RAM, återanslutningstid, fel och funktionstest. Ingen trimning accepteras om den försämrar Wi-Fi-stabilitet, touchrespons, ljud eller återställningsväg.
