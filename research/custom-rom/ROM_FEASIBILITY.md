# FarfarRemote OS ROM feasibility

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Executive assessment

- **Option A — stock-based Android 4.4.4 optimization: FEASIBLE, best near-term path. VERIFIED:** FarfarRemote works as a HOME launcher on Sony's vendor stack. Most useful low-risk gains are application-level polling/screen behavior and manually reversible Android settings. Removing protected system apps or editing `/system` is **BLOCKED** until a verified root/firmware path and dependency tests exist.
- **Option B — new AOSP/LineageOS ROM: NOT CURRENTLY BUILDABLE for exact E2003. UNKNOWN/BLOCKED:** no verified E2003 device tree, matching kernel config/source, vendor blob set, recovery tree, or reproducible ROM recipe was found. Sony's open-device program covers selected Xperia models; E2003 is not listed in the current Sony device tree set. A 2022 community response reports no official or unofficial LineageOS build at that time. A 2018 blog does claim a LineageOS 15.0 Oreo E4g beta, but describes it as based on a Samsung Galaxy Note 8 custom ROM and provides no source, exact variant matrix, hashes or reproducible evidence. It remains an unverified claim and does not supply build inputs. Current absence in searched repositories does not prove no private or abandoned work exists.
- **Option C — FarfarRemote dedicated system experience: ALREADY FEASIBLE as a launcher configuration, not a ROM. VERIFIED:** the existing OS flavor registers HOME, starts FarfarRemote and retains normal Android system services, Wi-Fi settings, USB/ADB and recovery routes. Direct Android bootanimation/init/service changes require root and a matching image and are **BLOCKED** for now.

## Base-version recommendation

Use stock Android 4.4.4/API 19 as the compatibility baseline now. No newer Android base is recommended until a device-specific ROM boots and passes screen/touch, Wi-Fi, audio, charging, USB/ADB, suspend/resume and Kodi tests. A 5.x/6.x MTK port is a theoretical target, not a demonstrated E2003 build. Newer OS support would require new vendor HALs/blobs, kernel compatibility, SELinux policy and working recovery; merely compiling AOSP is insufficient.

## Newly available image evidence

An unverified E2003 R10A Customized UK FTF has now yielded offline `boot` and `fotakernel` ELF payloads with their embedded SHA-256 checks passing. The boot payload includes a Linux 3.10.48+ kernel, Android init ramdisk, MediaTek fstab and Sony connectivity setup. This materially improves our understanding of the stock boot chain. It does **not** make a ROM buildable: the package CDA/revision are blank, it is not matched to the live `1293-7358 R7A`, its origin has no trusted independent checksum, and no exact kernel source/defconfig, device tree or complete vendor extraction is available. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md) for file-level evidence.

The extracted boot container is Sony ELF format rather than a standard Android `boot.img`. An Android boot header and a valid restore method have not been reconstructed. Magisk compatibility therefore remains untested despite having a candidate ramdisk to inspect.

## What a minimal dedicated build must keep

Android init/Binder/system_server; SurfaceFlinger and Mali/gralloc/hwcomposer; touchscreen/input; Package Manager and text input; Wi-Fi framework, vendor driver/firmware and supplicant; network stack; storage and media path; power, battery, thermal and charging services; USB gadget and ADB; Sony/MediaTek boot and board services; and Settings or a reliable alternative path for Wi-Fi/debugging. Bluetooth can be omitted only after confirming no external controls use it. Remove user apps only after package/service dependency and recovery tests.

## Expected engineering cost and benefits

A stock-based debloat might free user RAM/storage and reduce background wake/network traffic. It does not guarantee lower idle current or faster boot: Android LMK may use free memory as cache, and vendor services may be essential. A custom OS could reduce background work, but its cost is very high because the exact device support layer is missing. Any claim of runtime/boot improvement requires repeatable measurements on this same aging battery and device.

## Required bring-up milestones for a ROM

1. Exact stock FTF, boot/FOTA images and cryptographic inventory.
2. Matching GPL kernel source, defconfig, toolchain, boot image format and vendor modules.
3. Device tree/BoardConfig, init/fstab, partition map, proprietary userspace and firmware extraction scripts.
4. Offline recovery image build and boot-image parser verification.
5. Dedicated recovery path and recoverable boot test plan.
6. First experimental image, built and inspected offline, then separately authorized device boot testing.
7. Full hardware matrix: display/touch; orientation; Wi-Fi and reboot reconnection; Bluetooth if retained; audio; storage; charging/current/thermal; USB/ADB; deep sleep/wake; Kodi app and launcher.

Until milestones 1–5 are complete, focus on the proven stock launcher and app. No image built from unrelated E4g/E4/E2033 sources is an acceptable shortcut.
