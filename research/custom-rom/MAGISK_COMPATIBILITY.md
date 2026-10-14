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
- **UPDATED / VERIFIED for an unmatched analysis candidate:** the E2003-labelled R10A FTF contains `boot.sin`, whose verified SIN payload decodes to a Sony-format 32-bit ARM ELF (not Android `boot.img`). Its two load segments include a gzip-compressed 3.10.48+ kernel and an Android init cpio ramdisk. The candidate's internal build is `25.0.A.2.31_R10A CustomizedUK`, with blank CDA/revision, so it does not establish the installed `1293-7358 R7A` boot image.
- **MagiskBoot format limitation, VERIFIED from v18.1 source:** the official v18.1 `magiskboot` format detector recognizes ELF32 and `bootimg.cpp` exits with status 3 (`ELF32`) instead of unpacking it. The Sony `boot.sin` ELF therefore cannot be passed directly to this MagiskBoot parser. A conversion to Android boot-image format is required before patching, and the conversion must preserve Sony's boot semantics. The local boot-container POC has an Android boot header, but MagiskBoot has not been run against it.
- **Host caveat, VERIFIED locally:** the official [Magisk v18.1 release](https://github.com/topjohnwu/Magisk/releases/tag/v18.1) was downloaded for offline inspection; ZIP integrity passed and the observed ZIP SHA-256 is `795776a9e2345de553118e2e4cb13618a1fd262c0029b08c5ac3dcea52d07e73` (GitHub did not publish an asset digest). Its x86 `magiskboot` is a 32-bit Android ELF with interpreter `/system/bin/linker`, so it does not execute natively on this Linux Mint host. No Android binary was pushed to the phone. A host-native build/test remains **UNKNOWN**. See the exact [v18.1 parser source](https://github.com/topjohnwu/Magisk/blob/v18.1/native/jni/magiskboot/bootimg.cpp) and [format detector](https://github.com/topjohnwu/Magisk/blob/v18.1/native/jni/magiskboot/format.cpp).

## Is a Magisk patch technically feasible?

Potentially, but only conditionally. Magisk v18.1's Android floor includes KitKat, but a boot-image root method still needs the exact stock boot image, a confirmed unlocked bootloader, a patcher that accepts the image format, and a reliable way to restore the original. The owner reports unlock; live Fastboot has not confirmed it. ADB cannot read the protected boot block. The only extracted stock candidate is R10A with unknown CDA match and Sony ELF format, which MagiskBoot v18.1 explicitly refuses to unpack. Converting an exact R7A Sony ELF into a boot image would itself need a verified, semantics-preserving procedure. The existing generic container POC is not exact R7A and has not been tested with MagiskBoot or on-device.

Custom recovery is not conceptually required by Magisk's boot-image patch model if one can patch an exact stock boot image and safely restore/boot it through a verified bootloader path. On this exact handset, that path is **BLOCKED**. A recovery could help, but the only leads found are historical community builds and not verified for firmware 25.0.A.2.31/CDA 1293-7358 R7A.

## Recommendation

1. Keep the current system unmodified.
2. Obtain precise `1293-7358 R7A` E2003 firmware and identify a supported, source-audited Sony ELF-to-Android boot-image route, if one exists.
3. Test only copies offline; record source-image hashes and all conversion metadata before considering Magisk compatibility.
4. Only then compare against the official Magisk v22.1 patcher/source and determine whether its KitKat payload, ARMv7 ABI, SELinux policy and Sony init/ramdisk conventions are compatible.
5. Root is a separate device change. Do not install Magisk or flash a patched image as part of this research phase.

If the objective is only removing applications, prefer the reversible Android package controls already available without root where possible. Magisk is not a performance optimization by itself and adds boot-time code/services; any battery change must be measured.
