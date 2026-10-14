# Custom ROM research — Sony Xperia E4g E2003

This directory is a research record for the exact E2003 / Android 4.4.4 / firmware 25.0.A.2.31 target. It is not a flash guide. All device diagnostics performed for this set were read-only. No root, bootloader, partition, firmware, recovery or package modification was performed.

## Documents

- [DEVICE_HARDWARE.md](DEVICE_HARDWARE.md) — verified hardware, MTK identification discrepancy, variants and drivers.
- [DEVICE_TREE_BLOBS.md](DEVICE_TREE_BLOBS.md) — read-only R7A HAL/blob inventory, static dependencies, and mismatches in the candidate `callass` config.
- [MAGISK_COMPATIBILITY.md](MAGISK_COMPATIBILITY.md) — Android-version boundaries, MagiskBoot and feasibility.
- [ROOT_METHODS.md](ROOT_METHODS.md) — Magisk, KingRoot/KingoRoot, SuperSU and MTK method status.
- [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md) — official sources, firmware leads, provenance and offline extraction.
- [PARTITION_LAYOUT.md](PARTITION_LAYOUT.md) — read-only labels/sizes and protected areas.
- [ROM_FEASIBILITY.md](ROM_FEASIBILITY.md) — stock, custom ROM and dedicated system options.
- [BATTERY_OPTIMIZATION.md](BATTERY_OPTIMIZATION.md) — measurement evidence and safe A/B plan.
- [BUILD_ENVIRONMENT.md](BUILD_ENVIRONMENT.md) — host constraints and non-destructive helper tooling.
- [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md) — recovery blockers and prerequisites.
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) — staged gates and exact remaining blockers.

## Status meanings

- **VERIFIED** means observed on the exact phone or in an authoritative source.
- **REPORTED** means an owner/community statement not reproduced here.
- **UNKNOWN** means not established by evidence.
- **BLOCKED** means work cannot responsibly progress until named missing evidence/artifacts are obtained.

Do not commit stock firmware, boot/recovery/system images, proprietary vendor binaries, private device dumps, USB serials, Wi-Fi details or personal audit output. Scripts here never flash or write to the phone.
