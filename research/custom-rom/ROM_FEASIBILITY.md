# FarfarRemote OS ROM feasibility

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Executive assessment

- **Option A — stock-based Android 4.4.4 optimization: FEASIBLE, best near-term path. VERIFIED:** FarfarRemote works as a HOME launcher on Sony's vendor stack. Most useful low-risk gains are application-level polling/screen behavior and manually reversible Android settings. Removing protected system apps or editing `/system` is **BLOCKED** until a verified root/firmware path and dependency tests exist.
- **Option B — new AOSP/LineageOS ROM: NOT CURRENTLY BUILDABLE for exact E2003. UNKNOWN/BLOCKED:** no verified E2003 device tree, matching kernel config/source, recovery tree, or reproducible ROM recipe was found. A full E2003-labelled KitKat system image now exists locally as an unverified analysis candidate, so the matching firmware family gives us proprietary userspace/HAL material. This is not a source tree and does not solve kernel/device integration. Sony's open-device program covers selected Xperia models; E2003 is not listed in the current Sony device tree set. A 2022 community response reports no official or unofficial LineageOS build at that time. A 2018 blog does claim a LineageOS 15.0 Oreo E4g beta, but describes it as based on a Samsung Galaxy Note 8 custom ROM and provides no source, exact variant matrix, hashes or reproducible evidence. It remains an unverified claim and does not supply build inputs.
- **Stock-derived FarfarRemote system image: technically plausible to build offline; device success remains unproven.** The candidate `system.sin` reconstructs as a 2,097,152,000-byte ext4 image whose `/build.prop` identifies `E2003`, API 19, Android 4.4.4, firmware `25.0.A.2.31`, and customization `1293-7276 R10A`. The phone runs `1293-7358 R7A`, so this is not a matching system image. A historical TWRP image explicitly built for E2003 has now been retrieved and statically inspected. Its kernel is byte-identical to the R10A candidate's stock kernel and its fstab maps recovery to the live p9 partition. This is substantially stronger recovery/boot-stack evidence, but its R5A customization, unaudited provenance and untested behavior on live R7A still prevent calling it a safe restore path.
- **Option C — FarfarRemote dedicated system experience: ALREADY FEASIBLE as a launcher configuration, not a ROM. VERIFIED:** the existing OS flavor registers HOME, starts FarfarRemote and retains normal Android system services, Wi-Fi settings, USB/ADB and recovery routes. Direct Android bootanimation/init/service changes require root and a matching image and are **BLOCKED** for now.

## Base-version recommendation

Use stock Android 4.4.4/API 19 as the compatibility baseline now. No newer Android base is recommended until a device-specific ROM boots and passes screen/touch, Wi-Fi, audio, charging, USB/ADB, suspend/resume and Kodi tests. A 5.x/6.x MTK port is a theoretical target, not a demonstrated E2003 build. Newer OS support would require new vendor HALs/blobs, kernel compatibility, SELinux policy and working recovery; merely compiling AOSP is insufficient.

## Newly available image evidence

An unverified E2003 R10A Customized UK FTF has now yielded offline `boot`, `fotakernel` and `system` payloads. Embedded SIN SHA-256 checks passed. The reconstructed system image is the exact observed partition size; its build properties identify `1293-7276 R10A`, not the live `1293-7358 R7A`. A read-only `e2fsck` scan completes but reports an inode-bitmap padding warning, so we do not treat the filesystem check as fully clean. The boot payload includes a Linux 3.10.48+ kernel, Android init ramdisk, MediaTek fstab and Sony connectivity setup. This materially improves understanding of the stock stack and gives us a basis for offline file-level inspection. It does **not** authenticate the mirror or prove cross-CDA compatibility, provide kernel source/defconfig or device tree, or validate a restore/recovery path. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md) for file-level evidence.

The extracted boot container is Sony ELF format rather than a standard Android `boot.img`. An Android boot header and a valid restore method have not been reconstructed. Magisk compatibility therefore remains untested despite having a candidate ramdisk to inspect.

### Full live R7A versus candidate R10A `/system` tree comparison — 2026-10-14

The live E2003 was confirmed read-only over ADB as Android 4.4.4 / `25.0.A.2.31` / customization `1293-7358 R7A`. A full file-tree comparison against the extracted E2003 R10A candidate was run with [`tools/compare_system_trees.py`](tools/compare_system_trees.py). Counts: 4,320 R7A files, 4,283 R10A files, 4,263 common paths, 57 R7A-only and 20 R10A-only. **4,248/4,263 common paths (99.65%) are byte-identical.** Thirteen common files differ in size; fifteen differ in hash overall, meaning two additional same-size content differences. Differences include build/customization metadata, region-specific assets and Sony/Android overlays. The comparison is reproducible from captured trees; proprietary trees remain outside Git. This supersedes the earlier statement that a full pull was cancelled at ~354 MB: that statement described an earlier attempt; a later pull captured the file tree, except inaccessible `lost+found`. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).

This supports using the R10A package as a source of candidate files and confirms high userspace similarity. It is **not** proof that one complete image can replace the other: file metadata/labels, protected `lost+found`, partition layout, boot/FOTA, radio-specific state and boot behavior are not covered. The R10A `/build.prop` identifies `1293-7276 R10A`, not the installed CDA. Preserve R7A-specific files and do not wholesale replace `/system`.

### Retrieved E2003 recovery candidate — 2026-10-14

The archived XDA first post expressly identifies E2003, claims the TWRP functions were tested, and documents a recovery flash procedure. We retrieved the linked image and verified its Android boot-image header. Its embedded device/build properties identify E2003 / API 19 / `25.0.A.2.31`, and its kernel SHA-256 exactly matches the kernel segment in the R10A stock boot candidate. Its recovery fstab maps recovery to p9, which the live phone reports as `fotakernel`. The image is nevertheless a historical community artifact with customization R5A, no auditable source/build recipe or trusted checksum, and no independent test on this handset. No boot/flash/restore was attempted. It improves feasibility substantially but does not itself establish a rollback route.

The archived post and binary analysis are documented in [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md). Sony ELF-to-Android boot-image conversion and Magisk compatibility remain untested.

## What a minimal dedicated build must keep

Android init/Binder/system_server; SurfaceFlinger and Mali/gralloc/hwcomposer; touchscreen/input; Package Manager and text input; Wi-Fi framework, the observed `mt-wifi` driver/firmware and supplicant; network stack; storage and media path; power, battery, thermal and charging services; USB gadget and ADB; Sony/MediaTek boot and board services; and Settings or a reliable alternative path for Wi-Fi/debugging. Bluetooth can be omitted only after confirming no external controls use it. Remove user apps only after package/service dependency and recovery tests. The live stock system contains proprietary HAL/firmware artifacts, so a “minimal” image must preserve required components and respect their redistribution terms; exact dependencies are not fully mapped yet.

## Expected engineering cost and benefits

A stock-based debloat might free user RAM/storage and reduce background wake/network traffic. It does not guarantee lower idle current or faster boot: Android LMK may use free memory as cache, and vendor services may be essential. A custom OS could reduce background work, but its cost is very high because the exact device support layer is missing. Any claim of runtime/boot improvement requires repeatable measurements on this same aging battery and device.

## Required bring-up milestones for a ROM

1. Exact stock FTF, boot/FOTA images and cryptographic inventory. Current candidate is exact model/build-family but wrong CDA/revision and untrusted provenance.
2. Matching GPL kernel source, defconfig, toolchain and vendor modules; current image contains the proprietary userspace, but no matching source/config.
3. Device tree/BoardConfig, init/fstab, partition map and reproducible proprietary-file extraction scripts.
4. Audited E2003 recovery source/artifact and a proven non-permanent test-boot path (if the bootloader supports one).
5. Confirmed official or exact-firmware restore route plus a recoverable boot test plan.
6. First experimental image, built and inspected offline, then separately authorized device boot testing.
7. Full hardware matrix: display/touch; orientation; Wi-Fi and reboot reconnection; Bluetooth if retained; audio; storage; charging/current/thermal; USB/ADB; deep sleep/wake; Kodi app and launcher.

Until milestones 1–5 are complete, focus on the proven stock launcher and app. No image built from unrelated E4g/E4/E2033 sources is an acceptable shortcut. The current work raises confidence in **offline stock-image analysis**, not in a safe flash or successful boot.
