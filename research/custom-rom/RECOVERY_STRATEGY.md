# Recovery and restore strategy

## Current recovery position

- **VERIFIED:** Sony firmware exposes a `fotakernel` partition alias; there is no separately named `recovery` partition in the live read-only partition map.
- **REPORTED:** historical community posts link E4g TWRP builds/recovery instructions. A contemporaneous E4g forum discussion also notes boot-image unpacking problems. These artifacts have not been downloaded, hashed or tested against this E2003, build 25.0.A.2.31, CDA 1293-7358 R7A.
- **UNKNOWN:** whether bootloader supports `fastboot boot` of a recovery image, whether `fotakernel` is recovery-only/update storage on this firmware, and whether any exact E2003 TWRP can mount/decrypt this `/data`/system layout.
- **REPORTED:** owner says bootloader unlocked; no independent read-only Fastboot confirmation. Current USB connection is normal ADB mode.
- **VERIFIED service exists:** Sony Xperia Companion has a software repair feature on supported Windows/macOS clients. Whether it still serves exact E2003 25.0.A.2.31/CDA 1293-7358 R7A is unknown; repair may wipe data.

## Recovery route required before root or ROM

1. Find a traceable exact E2003 stock FTF/package, verify its archive and SHA-256, and inspect included `boot` and `fotakernel` SIN payloads.
2. Preserve original image copies and hashes offline, with two independent copies. The app's preferences can be backed up logically only through normal app UI/export; do not assume an image restore retains user data.
3. Verify Sony Companion repair availability for this model on the actual supported desktop OS, or establish an exact FTF restore method using documented Sony/Flashtool tooling. No actual repair/flash trial here.
4. Verify Fastboot identity and allowed read-only variables only when the owner deliberately places the device in that mode. Do not issue unlock, erase, flash, format or reboot commands as part of discovery.
5. Obtain a recovery image explicitly built for E2003 single-SIM and matching layout; inspect source, build recipe and checksums. Test first only if a safe temporary boot path is proven.
6. Before any separately authorized write, prepare a recovery checklist, charger/cable, host tools, exact image hash, rollback path and expected data-loss statement.

## Protected areas and constraints

Do not write `ta`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1` or `tee2`. Never use a generic MTK scatter/preloader package. Never flash E2033/E2043 dual-SIM or other Xperia/MT6732/MT6752 images.

No recovery image, stock firmware image or raw partition copy is in this repository. Until that changes, recovery readiness is **BLOCKED** and no root/custom ROM write is acceptable.
