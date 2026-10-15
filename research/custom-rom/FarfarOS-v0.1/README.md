# FarfarOS Experimental ROM v0.1

FarfarOS v0.1 is an offline, stock-derived **E2003 `/system` ext4 experiment**. It reconstructs the R7A system tree from the inspected E2003 R10A stock filesystem plus files captured read-only from the owner's R7A phone, then adds the existing FarfarRemote OS APK and the owner-supplied boot animation.

This is a development artifact, **not a complete ROM, not a Sony FTF/SIN package, not a recovery image, not boot-tested, and not approved for flashing**. It does not replace `boot`, `fotakernel`, `preloader`, NVRAM, TA, or any other partition. A successful host filesystem build does not prove that the phone can boot it.

## Current scope

- Base: Sony Android 4.4.4 / API 19, E2003 `25.0.A.2.31`, CDA `1293-7358 R7A` system-file state.
- Hardware stack: unchanged stock R7A userspace files are restored over a hash-pinned R10A ext4 candidate; no framework or driver rewrite.
- FarfarRemote: existing signed OS APK is inserted at `/app/FarfarRemote.apk`.
- Animation: owner-provided 540×960 `bootanimation.zip` is inserted at `/media/bootanimation.zip` with the captured R7A file metadata and SELinux label.
- Cleanup: no Sony, telephony, or Android packages are removed or disabled in this first build. This minimizes boot and hardware regression risk.
- Home app: the APK retains its existing HOME intent; default-launcher selection is left to Android unless separately established in the boot configuration.

## Build

See [BUILD.md](BUILD.md). Proprietary firmware, private ADB pulls, metadata, generated images, and checksums must stay outside the repository. Inputs are intentionally passed explicitly so the build cannot silently substitute another Xperia variant.

## Documents

- [Build procedure](BUILD.md)
- [System component policy](SYSTEM_COMPONENTS.md)
- [Boot sequence](BOOT_SEQUENCE.md)
- [Hardware compatibility](HARDWARE_COMPATIBILITY.md)
- [Experimental test plan](EXPERIMENTAL_TEST_PLAN.md)
- [Known limitations](KNOWN_LIMITATIONS.md)
- [Build report](BUILD_REPORT.md)
- [System-only experiment proposal](FLASH_EXPERIMENT_PROPOSAL.md) — review document, not an authorization or flashing procedure.

## Status vocabulary

- **Built offline**: host script completed and produced an artifact.
- **Filesystem validated**: ext4 structural check and file-level readback/hash checks passed.
- **Boot-image structure validated**: Android/Sony container bytes parse statically; this does not prove bootloader acceptance.
- **Exact-device compatible**: tested on this E2003/CDA/firmware combination.
- **Boot-tested**: image started on hardware.
- **Functionally tested**: Wi-Fi, touch, audio, charging, ADB, launcher, and Kodi behavior were exercised on hardware.

The first combined v0.1 `/system` image has been built offline and passes the static filesystem and payload checks listed in `BUILD_REPORT.md`. It has not been boot-tested and must not be described as flashable.
