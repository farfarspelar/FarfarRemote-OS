# Recovery and restore strategy

## Current recovery position

- **VERIFIED:** Sony firmware exposes a `fotakernel` partition alias; there is no separately named `recovery` partition in the live read-only partition map.
- **REPORTED, untrusted lead:** a 2017 E4g blog post links unsigned/signed TWRP ZIP files and describes installing them through the stock recovery's update path. It does not establish exact support for E2003 vs E2006/E2053, firmware 25.0.A.2.31, or CDA 1293-7358 R7A; the linked payloads have not been acquired, hashed, source-audited or tested. The described stock-recovery sideload is an exploit-like privileged installation path, not a safe read-only probe. Do not download-and-run or follow it as an install procedure.
- **REPORTED:** an XDA thread titled “TWRP recovery Sony Xperia E4g” is referenced by a contemporaneous E4g forum post. The thread is inaccessible through the current research browser, so its exact device variants, source and artifacts remain **UNKNOWN**.
- **VERIFIED community status report:** an /e/OS device request says there is no official or unofficial LineageOS build for the E4g as of April 2022. This is not proof no abandoned/private port ever existed, but it supports the present finding that there is no maintained public ROM baseline located for this model.
- **UNKNOWN:** whether bootloader supports `fastboot boot` of a recovery image, whether `fotakernel` is recovery-only/update storage on this firmware, and whether any exact E2003 TWRP can mount/decrypt this `/data`/system layout.
- **REPORTED:** owner says bootloader unlocked; no independent read-only Fastboot confirmation. Current USB connection is normal ADB mode.
- **VERIFIED service exists:** Sony Xperia Companion has a software repair feature on supported Windows/macOS clients. Whether it still serves exact E2003 25.0.A.2.31/CDA 1293-7358 R7A is unknown; repair may wipe data.

### Candidate image analysis update — 2026-10-14

An unverified mirror supplied an FTF whose internal manifest identifies `E2003`, build `25.0.A.2.31_R10A`, and `CustomizedUK`, but leaves both `cda` and `revision` blank. Its locally observed SHA-256 is `ffb5b42cc196eea4d6651817992bf230a3efdbef1e50ac68eb93866aeec8f37b`; the mirror provides no trusted comparison hash. ZIP CRC/integrity testing passed. This is **not** a match to the phone's `1293-7358 R7A` and is not an approved restore base.

The `boot.sin` and `fotakernel.sin` payloads were decoded offline and checked against their embedded SHA-256 values. Both are Sony-format ARM ELF images, not Android `boot.img` files. The boot ELF contains a 3.10.48+ kernel and an Android init cpio ramdisk; the FOTA ELF has a distinct FOTA ramdisk. This establishes an image-analysis lead only. It does not validate a recovery image, a bootloader path, or a safe image conversion. No `boot.img` conversion, patch, repack, or device write was attempted.

## Recovery route required before root or ROM

1. Find an independently traceable exact E2003 stock package matching CDA `1293-7358 R7A`; the R10A Customized UK mirror candidate is insufficient. Verify provenance/checksums and inspect included images offline.
2. Preserve original image copies and hashes offline, with two independent copies. The app's preferences can be backed up logically only through normal app UI/export; do not assume an image restore retains user data.
3. Verify Sony Companion repair availability for this model on the actual supported desktop OS, or establish an exact FTF restore method using documented Sony/Flashtool tooling. No actual repair/flash trial here.
4. Verify Fastboot identity and allowed read-only variables only when the owner deliberately places the device in that mode. Do not issue unlock, erase, flash, format or reboot commands as part of discovery.
5. Obtain a recovery image explicitly built for E2003 single-SIM and matching layout; inspect source, build recipe and checksums. Test first only if a safe temporary boot path is proven.
6. Before any separately authorized write, prepare a recovery checklist, charger/cable, host tools, exact image hash, rollback path and expected data-loss statement.

### Public recovery leads reviewed — 2026-10-14

- [Dian Ariyanto's 2017 E4g TWRP post](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/) links two ZIPs through third-party redirect/file hosts and describes temporary/permanent recovery installation. It provides no source repository, build identity, cryptographic digest or variant/CDA matrix. The page's broad “E4g” label is insufficient for the single-SIM E2003. Treat the files and procedure as **unverified and not approved**; in particular, do not test its stock-recovery sideload procedure on the phone.
- [XDA thread reference](https://xdaforums.com/t/twrp-recovey-sony-xperia-e4g-t3425174) was found linked from a contemporaneous forum post, but could not be fetched in this research session. No claim about its contents or compatibility is made.
- The [E4g /e/OS device request](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466) reports no official or unofficial LineageOS build in 2022. A separate [2018 blog post claiming an E4g LineageOS 15.0 Oreo beta](https://dianariyanto.com/install-custom-rom-sony-xperia-e4g-lineage-os-15-oreo/) exists. It says the port is based on a Samsung Galaxy Note 8 Oreo custom ROM and links ROM/GApps through third-party file hosts; it gives no source repository, exact E2003/E2006/E2053 compatibility, hash, build log or independently reproduced result. This establishes a **reported ROM claim**, not a verified E2003 ROM. We did not download or run it.

## Protected areas and constraints

Do not write `ta`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1` or `tee2`. Never use a generic MTK scatter/preloader package. Never flash E2033/E2043 dual-SIM or other Xperia/MT6732/MT6752 images.

No firmware or extracted image is in this repository. The R10A candidate exists only under `/tmp`, is unverified and mismatched/unknown at the CDA level. No tested recovery image or independently confirmed restore route exists. Recovery readiness remains **BLOCKED**; no root/custom ROM write is acceptable.
