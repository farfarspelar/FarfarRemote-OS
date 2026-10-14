# Magisk compatibility on Android 4.4.4

## Compatibility matrix

| Magisk line | Android support evidence | E2003 assessment |
|---|---|---|
| v18.1 | Official changelog explicitly says support down to Android 4.2 | KitKat is inside the stated OS floor. Device boot format and E2003 install behavior remain untested. |
| v19–v22.1 | Official changelog retains pre-5.0 support; v22.1 is the final release before v23 removes all pre-Android-5 support | **Best historical Magisk candidate for API 19 only if** boot image/ramdisk and install path are verified. Do not install yet. |
| v23–v25 | v23 removes all pre-Android-5.0 support | Not compatible with Android 4.4 as a supported install target. |
| v26+ / current | v26.0 explicitly raises minimum supported Android to 6.0; current README says devices higher than Android 6.0 | Not compatible with the stock E2003 OS. |

Sources: [official Magisk changelog](https://github.com/topjohnwu/Magisk/blob/master/docs/changes.md), [official Magisk README](https://github.com/topjohnwu/Magisk/blob/master/README.MD), [MagiskBoot tools documentation](https://github.com/topjohnwu/Magisk/blob/master/docs/tools.md).

## Important distinction: the app, root payload and boot parser

- **VERIFIED:** Magisk v18.1 changelog says Android 4.2 minimum. Magisk v23 removed all pre-Android-5 support; v26 raised the floor to Android 6.0. Thus newer official releases are not an answer for stock KitKat.
- **REPORTED/strong historical implication:** v22.1 is commonly identified as the final pre-Android-5 line. The changelog boundary is definitive for v23, but the exact v22.1 APK installation and every payload component must be checked from the official v22.1 release artifact before selection.
- **VERIFIED:** MagiskBoot is designed to unpack/repack boot images. Magisk v16.1 changelog specifically records a fix for MTK boot-image packaging. This is format support, not proof that this E2003 image parses or that Magisk's init/SU can boot correctly on the Sony firmware.
- **UNKNOWN:** no stock E2003 `boot.img` has been extracted, so the header version, kernel/ramdisk arrangement, compression, DTB, cmdline, page size and MagiskBoot result are unknown.
- **Host caveat:** Magisk release binaries target Android ABIs. Official Magisk build instructions support Linux x64 as a build host, but do not by themselves prove a released `magiskboot` executable can be run natively on this Linux workstation. Use AOSP's host-side [`unpack_bootimg.py`](https://android.googlesource.com/platform/system/tools/mkbootimg/+/927ff7988230147d5f54c7f78e261ad6f9d0f974/unpack_bootimg.py) for initial offline extraction, or build/verify a trusted host tool. Do not install a binary just because it is named `magiskboot`.

## Is a Magisk patch technically feasible?

Potentially, but only conditionally. A boot-image root method normally requires the exact stock boot image, an unlocked bootloader that accepts a compatible image, a matching patcher, and a reliable way to restore the exact original image. Here, owner reports an unlocked bootloader, but live Fastboot did not confirm it; ADB cannot read the protected boot block; no exact stock boot image or verified recovery is in the repository. The target is old non-A/B Android 4.4 and likely uses a classic boot ramdisk, but this remains an **inference**, not an observed image property.

Custom recovery is not conceptually required by Magisk's boot-image patch model if one can patch an exact stock boot image and safely restore/boot it through a verified bootloader path. On this exact handset, that path is **BLOCKED**. A recovery could help, but the only leads found are historical community builds and not verified for firmware 25.0.A.2.31/CDA 1293-7358 R7A.

## Recommendation

1. Keep the current system unmodified.
2. Obtain the precise E2003 stock firmware and inspect its `kernel.sin`/boot payload offline.
3. Identify the original boot image and test parsing on a copy with AOSP host tools; record SHA-256 and extracted metadata.
4. Only then compare against the official Magisk v22.1 patcher/source and determine whether its KitKat payload, ARMv7 ABI, SELinux policy and Sony init/ramdisk conventions are compatible.
5. Root is a separate device change. Do not install Magisk or flash a patched image as part of this research phase.

If the objective is only removing applications, prefer the reversible Android package controls already available without root where possible. Magisk is not a performance optimization by itself and adds boot-time code/services; any battery change must be measured.
