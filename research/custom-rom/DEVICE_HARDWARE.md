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
| OS/build | Android 4.4.4, API 19; build 25.0.A.2.31; customization 1293-7358 R7A | **VERIFIED**, read-only live properties. Specifically, `ro.semc.version.cust=1293-7358` and `ro.semc.version.cust_revision=R7A`; separate `ro.semc.version.sw=1292-0502` / `sw_variant=GENERICSS` values describe the software base and are not the CDA. |
| SoC marketed by Sony | MediaTek MT6732, quad-core 1.5 GHz | **VERIFIED** by Sony white paper |
| Vendor platform string | `ro.hardware=mt6752`; `/proc/cpuinfo` says Hardware MT6752 | **VERIFIED** observation; its relationship to the marketed MT6732 SKU is **UNKNOWN**. Do not infer MT6752-device image compatibility. |
| CPU | ARMv7, architecture 7, 32-bit ABI `armeabi-v7a`/`armeabi`; CPU reports ARMv7 features including NEON/VFP | **VERIFIED**, live properties and `/proc/cpuinfo` |
| GPU | ARM Mali-760 MP2 per Sony; `/system/lib/libGLES_mali.so`, `gralloc.mt6752.so`, `hwcomposer.mt6752.so` are present | Sony specs and live file listing **VERIFIED**; source/redistribution rights and exact binary interfaces remain separate questions |
| RAM | Sony says 1 GB; live `MemTotal` 918,424 kB | **VERIFIED** |
| Flash | Sony says up to 8 GB; live `mmcblk0` reports 7,634,944 1-KiB blocks (nominal 8-GB class storage). `/data` mounted capacity reported 4.8 GB. | **VERIFIED** as visible capacity; exact eMMC vendor/model and wear are **UNKNOWN** |
| Display | 4.7-inch TFT, 540×960, capacitive multi-touch | **VERIFIED**, Sony white paper |
| Kernel | Linux 3.10.48+, GCC 4.8, Sony build dated 2015-09-08 | **VERIFIED**, live `/proc/version` |
| Board / product device | `ro.product.board=callass`; product device `E2003` | **VERIFIED**, live read-only properties. Exact kernel source target for `callass` remains **UNKNOWN**. |
| CPU core ID | `/proc/cpuinfo`: ARM implementer `0x41`, part `0xd03`; Arm identifies part `0xd03` as Cortex-A53. Sony specifies a quad-core SoC. | Live ID **VERIFIED**; interpretation **VERIFIED** by [Arm's Cortex-A53 technical reference manual](https://documentation-service.arm.com/static/6040c321ee937942ba301626). Device runs a 32-bit ARMv7 kernel/userspace despite the core family's ARMv8 capability. At the latest capture `/sys/devices/system/cpu` reported `possible=0-3`, `present=0-3`, `online=0`, `offline=1-3`, while `/proc/cpuinfo` exposed only processor 0; this is a time-specific runtime state, not a claim the hardware has one core. |
| Bootloader | Read-only Fastboot identified product `E2003`, version `1290-9780 S1_Boot_MT6732_TC9PRA_9`, `secure: yes`; `getvar unlocked` was blank and `oem device-info` returned unknown command. | Product/version **VERIFIED** in Fastboot on 2026-10-14. Owner reports unlocked; unlock state remains **REPORTED/UNKNOWN**, because these queries did not confirm it. `secure: yes` alone is not interpreted as locked/unlocked. |
| Recovery | Partition table has `fotakernel` but no partition labelled `recovery`; both `boot` and `fotakernel` are 32,768 1-KiB blocks. | **VERIFIED** names/sizes; which recovery path firmware uses and whether an image can be booted temporarily are **UNKNOWN** |
| Graphics stack | Live `/system/lib/hw` contains `gralloc.mt6752.so` and `hwcomposer.mt6752.so`; `/system/lib/egl/libGLES_mali.so` is about 18.7 MB | **VERIFIED** file presence/size. Source revision, interface compatibility and redistribution rights are **UNKNOWN**; file size is not RAM use. |
| Wi-Fi | Live interface is `wlan0`; sysfs binds it to platform driver `mt-wifi`. Firmware/configuration assets are present in `/system/lib/hw` and `/system/etc/firmware` | **VERIFIED** runtime interface/driver name and file presence. Exact chipset revision, source and blob set are **UNKNOWN**. Preserve the stock driver/firmware path for any stock-based OS. |
| Bluetooth/audio hardware modules | `/system/lib/hw` contains `bluetooth.default.so` and audio HAL modules | **VERIFIED** file presence only. This does not by itself prove Bluetooth operation or all audio paths in a new ROM. |

Primary Sony references: [E4g white paper](https://www-support-downloads.sonymobile.com/e2003/whitepaper_EN_e2003_e2006_e2053_xperia_E4g.pdf) and [E2003/E2006/E2053 user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf).

## Partition and boot architecture clues

Read-only aliases in `/dev/block/platform/mtk-msdc.0/by-name` map to `mmcblk0p1` through `p22`; the detailed table is in [PARTITION_LAYOUT.md](PARTITION_LAYOUT.md). The block access policy denied reading even one byte of the `boot` partition as ADB shell. No raw boot/recovery/TA/NVRAM data was read. `/system` is mounted read-only.

`ro.bootloader=s1` and the Sony `fotakernel` naming establish Sony/MTK-specific boot layout clues, not a validated flashing protocol. The host currently sees the handset in normal ADB mode. A temporary Fastboot identity probe was performed and is documented below; no write operation was performed.

## Variant boundaries

Sony's white paper documents the E2003, E2006 and E2053 as distinct network SKUs with different LTE/UMTS bands. The Sony user guide groups those three single-SIM models, while E2033/E2043 belong to the dual-SIM family and separate documentation/firmware listings. Similar casing, SoC family, resolution or marketing name does not establish a compatible boot image, modem/NVRAM data, partition map, device tree or recovery.

**Rule:** only accept a firmware/recovery/kernel artifact explicitly identified for E2003 and then verify its build/CDA and image metadata. Never substitute E2033/E2043 or another MT67xx device.

## Display, Wi-Fi and platform drivers

The running firmware exposes Mali EGL/GLES, MediaTek gralloc and hardware-composer modules; Wi-Fi uses the `mt-wifi` platform driver and the `wlan0` interface. Firmware/configuration files and Bluetooth/audio HAL libraries are present under `/system`. Wi-Fi works on stock and reconnects after reboot per owner test. Exact driver source revisions, complete firmware blobs, calibration data, power profiles and kernel configuration have not been collected. These are **BLOCKED** for a reproducible ROM until matching stock firmware/source is available. The live proprietary stack is an important reason to prefer a stock-based dedicated image over a speculative AOSP port.

## Read-only package/root snapshot — 2026-10-14

The readiness script matched E2003/build `25.0.A.2.31`; ADB shell is UID 2000, no `su` command was found on its PATH, and no Fastboot device was connected. `pm list packages -d` reported `com.sonyericsson.startupflagservice` and `com.sonymobile.usm`. Follow-up `dumpsys package` showed user state `enabled=2` for the first and `enabled=0` (default) for the second. Their origin/status history is **UNKNOWN**; this inspection changed neither package. Do not treat this list as permission to disable or restore anything.

## Firmware boot-image analysis candidate — 2026-10-14

The unverified R10A Customized UK FTF described in [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md) was inspected offline. Its `boot.sin` payload has a verified embedded SHA-256 and decodes to a 32-bit ARM ELF with two load segments. The first segment's embedded kernel string reports Linux `3.10.48+`, GCC 4.8, build date 2015-09-08. The second is a gzip-compressed cpio ramdisk containing Android init scripts, `fstab`, `adbd`, and Sony/MediaTek setup. The FOTA image shares the same kernel bytes but contains a separate FOTA ramdisk. This is **VERIFIED for the downloaded file only**, not for the phone's installed R7A customization.

The candidate ramdisk's `init.mt6752.rc` and `/proc/version` naming align with the live `mt6752` platform string. This helps explain the board label; it does not establish a compatible board variant or authorize use of that image. The live firmware's CDA remains `1293-7358 R7A`, while candidate manifest CDA/revision are blank.

## Additional read-only prerequisite capture — 2026-10-14

The latest normal-Android ADB capture confirms `ro.product.board=callass`, `ro.hardware=mt6752`, `ro.mediatek.platform=MT6752`, `ro.bootloader=s1`, Linux `3.10.48+` built with GCC 4.8 on 2015-09-08, and CPU part `0xd03` (Cortex-A53). The runtime kernel is 32-bit ARMv7 with NEON/VFP; preserve an ARM 32-bit kernel/userspace toolchain unless source evidence proves otherwise. Sony specifies quad-core hardware, and sysfs lists CPUs 0–3 as possible/present. At this snapshot only CPU0 was online and CPUs1–3 were offline; the reason/state transition behavior is **UNKNOWN** and should be rechecked under load and after a cold boot before drawing power/performance conclusions.

`/proc/cmdline` access is denied to ADB shell, `/proc/config.gz` is absent, and `/proc/device-tree` plus `/sys/firmware/devicetree/base` are absent. `/system/lib/modules` is present but empty; the live Wi-Fi interface `wlan0` is attached to platform device `180f0000.WIFI` with driver name `mt-wifi`. This suggests the Wi-Fi path is built into the running kernel or otherwise supplied outside that directory; exact implementation is **UNKNOWN** without kernel source/config. No module was loaded, changed or removed.

CPU0 reported the `mt-cpufreq` driver with `interactive` governor, available range 468,000–1,495,000 kHz, current 1,170,000 kHz at capture. This is a single momentary sysfs reading, not a load or battery benchmark. The current `/proc/partitions` read reconfirms a 7,634,944 KiB eMMC block device, 2,048,000 KiB system partition, 32,768 KiB each for boot and fotakernel, and 5,168,640 KiB userdata. These are metadata only. No block contents were read in this capture. Live `MemTotal` is 918,424 kB.

### Fastboot identity probe — 2026-10-14

After confirming the ADB model/build, the phone was temporarily rebooted into Fastboot for read-only queries and returned with `fastboot reboot`; ADB then reconfirmed the same E2003 / `25.0.A.2.31` / `1293-7358 R7A` identity. Fastboot returned product `E2003`, bootloader `1290-9780 S1_Boot_MT6732_TC9PRA_9`, and `secure: yes`. `getvar unlocked` was empty, `max-download-size` and `variant` were empty, and `fastboot oem device-info` returned `unknown command`. No image was sent and no write command was used. These results verify transport/product/bootloader version but **do not** verify unlocked state or `fastboot boot` support.

The extracted files remain in `/tmp`; proprietary images/blobs have not been added to Git. No flashable Android `boot.img` was produced. The ELF/kernel payload has no embedded `IKCFG_ST`/`IKCFG_ED` kernel config markers. Sony's public kernel-copyleft branch inventory has no matching 25.0.A/E2003 branch, and no `callass` defconfig was found. The Sony ELF container's segments do not by themselves reveal a fully validated Android boot header or restore procedure.

## Current conclusion

The phone is a usable stock-based dedicated remote, but it is not yet a buildable ROM target. We have a valuable offline image-analysis candidate, but still lack an authenticated matching R7A stock image set, exact E2003 kernel config/source, device tree, complete proprietary blobs and a proven recovery route. The board-string discrepancy is better explained by the candidate's MT6752-labelled platform files, but exact single-SIM board compatibility remains unproven.
