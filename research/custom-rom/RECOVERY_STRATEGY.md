# Recovery and restore strategy

## Current recovery position

- **VERIFIED:** Sony firmware exposes a `fotakernel` partition alias; there is no separately named `recovery` partition in the live read-only partition map.
- **REPORTED, untrusted lead:** a 2017 E4g blog post links unsigned/signed TWRP ZIP files and describes installing them through the stock recovery's update path. It does not establish exact support for E2003 vs E2006/E2053, firmware 25.0.A.2.31, or CDA 1293-7358 R7A; the linked payloads have not been acquired, hashed, source-audited or tested. The described stock-recovery sideload path is not a safe read-only probe. Do not run it.
- **REPORTED, stronger exact-family lead:** an XDA thread titled “TWRP recovery Sony Xperia E4g” (2016) is linked by E4g owner forums. Later forum posts in the E4g/E4g dual thread report TWRP installed on both E2003 and E2033 devices, and report a recovery-related bootloop in another case. This supports that a community recovery existed for the family, but the underlying XDA attachment/build recipe is currently inaccessible and neither the binary nor its exact firmware/model compatibility has been verified. Treat it as a lead only, not a recovery image.
- **VERIFIED community status report:** an /e/OS device request says there is no official or unofficial LineageOS build for the E4g as of April 2022. This is not proof no abandoned/private port ever existed, but it supports the present finding that there is no maintained public ROM baseline located for this model.
- **UNKNOWN:** whether bootloader supports `fastboot boot` of a recovery image, whether `fotakernel` is recovery-only/update storage on this firmware, and whether any exact E2003 TWRP can mount/decrypt this `/data`/system layout.
- **REPORTED:** owner says bootloader unlocked; no independent read-only Fastboot confirmation. Current USB connection is normal ADB mode.
- **VERIFIED official route exists, exact restore unverified:** Sony's E4g support page lists Xperia Companion, and Sony's current Companion support page says Software Repair is supported across Xperia models. Sony's repair guidance warns that device data is deleted. **UNKNOWN:** whether the current repair flow still recognizes this specific E2003 and what build/CDA it downloads; it is not confirmed to restore 25.0.A.2.31 or CDA 1293-7358 R7A. Official desktop support is Windows/macOS, not Linux Mint.

### Candidate image analysis update — 2026-10-14

An unverified mirror supplied an FTF whose internal manifest identifies `E2003`, build `25.0.A.2.31_R10A`, and `CustomizedUK`, but leaves both `cda` and `revision` blank. Its locally observed SHA-256 is `ffb5b42cc196eea4d6651817992bf230a3efdbef1e50ac68eb93866aeec8f37b`; the mirror provides no trusted comparison hash. ZIP CRC/integrity testing passed. This is **not** a match to the phone's `1293-7358 R7A` and is not an approved restore base.

The `boot.sin` and `fotakernel.sin` payloads were decoded offline and checked against their embedded SHA-256 values. Both are Sony-format ARM ELF images, not Android `boot.img` files. The boot ELF contains a 3.10.48+ kernel and an Android init cpio ramdisk; the FOTA ELF has a distinct FOTA ramdisk. This establishes an image-analysis lead only. It does not validate a recovery image, a bootloader path, or a safe image conversion. No `boot.img` conversion, patch, repack, or device write was attempted.

## Recovery route required before root or ROM

1. **Promising official route to validate:** on a supported Windows/macOS host, inspect the current Xperia Companion repair flow for E2003 while stopping before the final confirmation that starts repair. Record whether it recognizes E2003 and any offered software/customization metadata. Do not start repair during this preflight. A later actual repair test would erase device data and needs separate explicit authorization.
2. Find an independently traceable exact E2003 stock package matching CDA `1293-7358 R7A`; the R10A Customized UK mirror candidate is insufficient. Verify provenance/checksums and inspect included images offline.
3. Preserve original image copies and hashes offline, with two independent copies. The app's preferences can be backed up logically only through normal app UI/export; do not assume an image restore retains user data.
4. Establish what Sony Companion would restore and whether it is adequate as a recovery route, or establish an exact FTF restore method using documented Sony/Flashtool tooling. No actual repair/flash trial here.
5. Verify Fastboot identity and allowed read-only variables only when the owner deliberately places the device in that mode. Do not issue unlock, erase, flash, format or reboot commands as part of discovery.
6. Obtain a recovery image explicitly built for E2003 single-SIM and matching layout; inspect source, build recipe and checksums. Test first only if a safe temporary boot path is proven.
7. Before any separately authorized write, prepare a recovery checklist, charger/cable, host tools, exact image hash, rollback path and expected data-loss statement.

### Public recovery leads reviewed — 2026-10-14

- Sony's [Xperia E4g support page](https://www.sony.com.au/electronics/support/mobile-phones-tablets-mobile-phones/xperia-e4g) lists Xperia Companion among product support resources. Sony's [current Xperia Companion information](https://www.sony.jp/xperia/support/software/xperia-companion/) identifies Software Repair as supported; neither page specifies the firmware/CDA the repair flow will install on this retired E2003. Sony's repair process deletes device data. This is a better recovery lead than an unverified mirror, but not yet a validated restore base.

- [Dian Ariyanto's 2017 E4g TWRP post](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/) links two ZIPs through third-party redirect/file hosts and describes temporary/permanent recovery installation. It provides no source repository, build identity, cryptographic digest or variant/CDA matrix. The page's broad “E4g” label is insufficient for the single-SIM E2003. Treat the files and procedure as **unverified and not approved**; do not test its stock-recovery sideload procedure on the phone.
- The [XDA TWRP thread](https://xdaforums.com/t/twrp-recovey-sony-xperia-e4g-t3425174) is corroborated by [E4g owner-forum reports](https://4pda.to/forum/index.php?showtopic=668811&st=480) saying users installed TWRP on E2003; the thread itself and binary are not currently retrievable for audit. This raises recovery feasibility, but does not verify an image for this exact firmware/CDA or prove a safe temporary-boot route.
- The [E4g /e/OS device request](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466) reports no official or unofficial LineageOS build in 2022. A separate [2018 blog post claiming an E4g LineageOS 15.0 Oreo beta](https://dianariyanto.com/install-custom-rom-sony-xperia-e4g-lineage-os-15-oreo/) exists. It says the port is based on a Samsung Galaxy Note 8 Oreo custom ROM and links ROM/GApps through third-party file hosts; it gives no source repository, exact E2003/E2006/E2053 compatibility, hash, build log or independently reproduced result. This establishes a **reported ROM claim**, not a verified E2003 ROM. We did not download or run it.

### Current device-side read-only status — 2026-10-14

ADB still sees one authorized device with USB product/model/device `E2003`. Android properties confirm build `25.0.A.2.31`, customization `1293-7358 R7A`. The read-only by-name map exposes `boot` (`mmcblk0p10`) and `fotakernel` (`mmcblk0p9`) but no separate partition named `recovery`; this is consistent with the candidate's Sony boot/FOTA arrangement, but does not prove how this bootloader selects recovery. The ADB shell cannot read raw partition contents. `ro.boot.flash.locked` and `ro.boot.verifiedbootstate` are empty in normal Android mode; the owner's unlocked report remains **REPORTED**, not independently verified. We did not reboot to Fastboot or issue any partition command.

The 42/42 sampled R7A/R10A system-file matches improve confidence in the candidate's *userspace relevance*, not the recovery path. The exact restore/recovery gate remains **BLOCKED**. A historical E4g TWRP mention is not enough to authorize or safely try an image.

## Protected areas and constraints

Do not write `ta`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1` or `tee2`. Never use a generic MTK scatter/preloader package. Never flash E2033/E2043 dual-SIM or other Xperia/MT6732/MT6752 images.

No firmware or extracted image is in this repository. The R10A candidate exists only under `/tmp`, is unverified and mismatched/unknown at the CDA level. No tested recovery image or independently confirmed restore route exists. Recovery readiness remains **BLOCKED**; no root/custom ROM write is acceptable.
