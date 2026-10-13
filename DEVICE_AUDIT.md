# Enhetsrevision – Sony Xperia E4g E2003

Datum: 2026-10-13. Detta är första arbetsfasens skrivskyddade revision.

## Rapporterad hårdvara (ännu ej direkt avläst)

| Fält | Uppgift | Status |
|---|---|---|
| Modell | Sony Xperia E4g E2003 | Angivet av användaren |
| Firmware | 25.0.A.2.31, Android 4.4.4, API 19 | Angivet; firmwarefamiljen stöds av firmwareindex från tredje part |
| SoC/ABI | MediaTek MT6732, armeabi-v7a | Angivet av användaren |
| RAM/skärm | cirka 897 MiB; 540×960, 240 dpi | Angivet av användaren |
| Bootloader | S1_Boot_MT6732_TC9PRA_9; unlock allowed YES | Angivet av användaren; ej självständigt verifierat |

## Arbetsmiljö och anslutning

- Arbetskatalogen saknar projektfiler och Git-repositorymetadata.
- `/usr/bin/fastboot` finns. `fastboot devices -l` returnerade ingen enhet.
- `/usr/bin/adb` är Android Debug Bridge 1.0.41, platform-tools 34.0.4-debian. ADB-server kunde inte startas: lokal smartsocket-bindning gav `Operation not permitted`.
- `/dev/bus/usb` saknas i den här exekveringsmiljön och libusb kunde inte initieras (`-99`). Detta betyder att Codex-miljön saknar synlig USB-enhetsåtkomst; det bevisar inte att värddatorn eller telefonen saknar fungerande USB.
- Inga kommandon skickades till enheten; inga partitioner eller inställningar ändrades.

## Nödvändig fältinventering

När USB är tillgänglig på värddatorn, dokumentera först `adb devices -l`, `getprop`, `df`, `dumpsys meminfo`, `dumpsys activity` och `dumpsys package` utan att modifiera systemet. Samla `/proc/last_kmsg` eller `dmesg` endast om behörighet finns. Identifiera paketnamn, tjänster och processer samt beroenden via manifest, intent providers, delade UID, privileged permissions och loggar. Gör en initial kallstartsmätning med video/tidsstämpel och upprepa minst fem gånger.

## Säkerhetskritisk information

Spara exakt firmwareversion/region, build fingerprint, bootloaderstatus, partitionstabell och tillgängliga Sony-återställningspaket innan förändring. Rör inte preloader, NVRAM, modem/calibration, RPMB eller andra unika/säkerhetskritiska områden. Att telefonidata får raderas innebär inte tillstånd att riskera identitets- eller radiokalibreringsdata.
