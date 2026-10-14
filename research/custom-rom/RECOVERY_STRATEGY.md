# Recovery and restore strategy

## Current recovery position

- **VERIFIED:** Sony firmware exposes a `fotakernel` partition alias; there is no separately named `recovery` partition in the live read-only partition map.
- **REPORTED:** historical community posts link E4g TWRP builds/recovery instructions. A contemporaneous E4g forum discussion also notes boot-image unpacking problems. These artifacts have not been downloaded, hashed or tested against this E2003, build 25.0.A.2.31, CDA 1293-7358 R7A.
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

## Protected areas and constraints

Do not write `ta`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1` or `tee2`. Never use a generic MTK scatter/preloader package. Never flash E2033/E2043 dual-SIM or other Xperia/MT6732/MT6752 images.

No firmware or extracted image is in this repository. The R10A candidate exists only under `/tmp`, is unverified and mismatched/unknown at the CDA level. No tested recovery image or independently confirmed restore route exists. Recovery readiness remains **BLOCKED**; no root/custom ROM write is acceptable.
