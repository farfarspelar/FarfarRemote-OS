# FarfarOS Experimental ROM v0.1

FarfarOS v0.1 is a stock-derived **E2003 `/system` ext4 experiment**. It reconstructs the R7A system tree from the inspected E2003 R10A stock filesystem plus files captured read-only from the owner's R7A phone, then adds the existing FarfarRemote OS APK and the owner-supplied boot animation. The exact experimental image has now booted on the owner's E2003; the owner confirmed Wi-Fi and Kodi control work in a first smoke test. See [BUILD_REPORT.md](BUILD_REPORT.md) for tested scope and remaining checks.

This remains a development artifact, **not a complete ROM, Sony FTF/SIN package, or recovery image**. It was installed to the E2003 `system` partition under the owner's explicit approval and has booted with a user-confirmed Wi-Fi/Kodi smoke test. It does not replace `boot`, `fotakernel`, `preloader`, NVRAM, TA, or any other partition. The experimental status and incomplete regression coverage mean it is not a general-purpose flash package.

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
- [`preflight_e2003_system_write.sh`](../tools/preflight_e2003_system_write.sh) — read-only validation for the exact candidate image and a connected E2003 Fastboot target; never writes to the device.

## Status vocabulary

- **Built offline**: host script completed and produced an artifact.
- **Filesystem validated**: ext4 structural check and file-level readback/hash checks passed.
- **Boot-image structure validated**: Android/Sony container bytes parse statically; this does not prove bootloader acceptance.
- **Exact-device compatible**: tested on this E2003/CDA/firmware combination.
- **Boot-tested**: image started on hardware.
- **Functionally tested**: Wi-Fi, touch, audio, charging, ADB, launcher, and Kodi behavior were exercised on hardware.

The combined v0.1 `/system` image passed offline filesystem and payload checks and has now booted on the target E2003. The owner confirmed FarfarRemote launch, network association and Kodi control. This is a successful device smoke test, not complete hardware qualification or validation of a reusable installer.
