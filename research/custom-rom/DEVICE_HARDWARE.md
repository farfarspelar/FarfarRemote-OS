# Xperia E4g E2003 hardware audit

Research date: 2026-10-14. This document is specific to the connected single-SIM E2003 running firmware 25.0.A.2.31.

## Evidence labels

- **VERIFIED**: read directly from the connected phone or an official Sony product document.
- **REPORTED**: owner or historical community statement not independently reproduced.
- **UNKNOWN**: not exposed by available read-only interfaces or not matched to an exact artifact.
- **BLOCKED**: cannot be established until the matching image/source/recovery is obtained.

## Hardware facts

| Item | Finding | Evidence |
|---|---|---|
| Model | Sony Xperia E4g E2003, single SIM | **VERIFIED**, live `ro.product.model/device`; Sony groups E2003/E2006/E2053 in the user guide |
| OS/build | Android 4.4.4, API 19; build 25.0.A.2.31; customization 1293-7358 R7A | **VERIFIED**, live properties and prior read-only audit |
| SoC marketed by Sony | MediaTek MT6732, quad-core 1.5 GHz | **VERIFIED** by Sony white paper |
| Vendor platform string | `ro.hardware=mt6752`; `/proc/cpuinfo` says Hardware MT6752 | **VERIFIED** observation; its relationship to the marketed MT6732 SKU is **UNKNOWN**. Do not infer MT6752-device image compatibility. |
| CPU | ARMv7, architecture 7, 32-bit ABI `armeabi-v7a`/`armeabi`; CPU reports ARMv7 features including NEON/VFP | **VERIFIED**, live properties and `/proc/cpuinfo` |
| GPU | ARM Mali-760 MP2 per Sony; `/system/lib/libGLES_mali.so`, `gralloc.mt6752.so`, `hwcomposer.mt6752.so` are present | Sony specs and live file listing **VERIFIED**; source/redistribution rights and exact binary interfaces remain separate questions |
| RAM | Sony says 1 GB; live `MemTotal` 918,424 kB | **VERIFIED** |
| Flash | Sony says up to 8 GB; live `mmcblk0` reports 7,634,944 1-KiB blocks (nominal 8-GB class storage). `/data` mounted capacity reported 4.8 GB. | **VERIFIED** as visible capacity; exact eMMC vendor/model and wear are **UNKNOWN** |
| Display | 4.7-inch TFT, 540×960, capacitive multi-touch | **VERIFIED**, Sony white paper |
| Kernel | Linux 3.10.48+, GCC 4.8, Sony build dated 2015-09-08 | **VERIFIED**, live `/proc/version` |
| Bootloader | `ro.bootloader=s1`; owner reports unlocked; live ADB shell is UID 2000. On 2026-10-14 the phone was in normal ADB mode, so this read-only check did not query Fastboot. Earlier Fastboot `getvar unlocked`/`oem device-info` did not confirm unlock. | Property **VERIFIED**; unlocked state **REPORTED**, independent confirmation **UNKNOWN** |
| Recovery | Partition table has `fotakernel` but no partition labelled `recovery`; both `boot` and `fotakernel` are 32,768 1-KiB blocks. | **VERIFIED** names/sizes; which recovery path firmware uses and whether an image can be booted temporarily are **UNKNOWN** |

Primary Sony references: [E4g white paper](https://www-support-downloads.sonymobile.com/e2003/whitepaper_EN_e2003_e2006_e2053_xperia_E4g.pdf) and [E2003/E2006/E2053 user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf).

## Partition and boot architecture clues

Read-only aliases in `/dev/block/platform/mtk-msdc.0/by-name` map to `mmcblk0p1` through `p22`; the detailed table is in [PARTITION_LAYOUT.md](PARTITION_LAYOUT.md). The block access policy denied reading even one byte of the `boot` partition as ADB shell. No raw boot/recovery/TA/NVRAM data was read. `/system` is mounted read-only.

`ro.bootloader=s1` and the Sony `fotakernel` naming establish Sony/MTK-specific boot layout clues, not a validated flashing protocol. The host currently sees the handset in normal ADB mode, not Fastboot. Do not issue reboot or write commands for this research.

## Variant boundaries

Sony's white paper documents the E2003, E2006 and E2053 as distinct network SKUs with different LTE/UMTS bands. The Sony user guide groups those three single-SIM models, while E2033/E2043 belong to the dual-SIM family and separate documentation/firmware listings. Similar casing, SoC family, resolution or marketing name does not establish a compatible boot image, modem/NVRAM data, partition map, device tree or recovery.

**Rule:** only accept a firmware/recovery/kernel artifact explicitly identified for E2003 and then verify its build/CDA and image metadata. Never substitute E2033/E2043 or another MT67xx device.

## Display, Wi-Fi and platform drivers

The running firmware exposes Mali EGL/GLES, MediaTek gralloc and hardware-composer modules; Wi-Fi works on stock and reconnects after reboot per owner test. Exact driver source revisions, firmware blobs, calibration data, power profiles and kernel configuration have not been collected. These are **BLOCKED** for a reproducible ROM until matching stock firmware/source is available.

## Read-only package/root snapshot — 2026-10-14

The readiness script matched E2003/build `25.0.A.2.31`; ADB shell is UID 2000, no `su` command was found on its PATH, and no Fastboot device was connected. `pm list packages -d` reported `com.sonyericsson.startupflagservice` and `com.sonymobile.usm`. Follow-up `dumpsys package` showed user state `enabled=2` for the first and `enabled=0` (default) for the second. Their origin/status history is **UNKNOWN**; this inspection changed neither package. Do not treat this list as permission to disable or restore anything.

## Current conclusion

The phone is a usable stock-based dedicated remote, but it is not yet a buildable ROM target. Missing items include an authenticated matching stock FTF/image set, extracted boot and recovery/FOTA images, E2003-specific kernel config/device tree, complete proprietary blobs and a proven recovery route. The board-string discrepancy must be resolved from the exact firmware/board source before compiling or porting a kernel.
