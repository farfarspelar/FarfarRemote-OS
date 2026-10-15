# FarfarRemote OS ROM feasibility

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Executive assessment

- **Option A — stock-based Android 4.4.4 optimization: FEASIBLE, best near-term path. VERIFIED:** FarfarRemote works as a HOME launcher on Sony's vendor stack. Most useful low-risk gains are application-level polling/screen behavior and manually reversible Android settings. Removing protected system apps or editing `/system` is **BLOCKED** until a verified root/firmware path and dependency tests exist.
- **Option B — new AOSP/LineageOS ROM: NOT CURRENTLY BUILDABLE as a complete product for exact E2003. UNKNOWN/BLOCKED:** a public mirror contains Linux 3.10.48 and `callass`/MT6752 32-bit configuration, and we successfully built its offline ARM `zImage` with NDK r10e GCC 4.8. The mirror's Sony provenance is reported but unauthenticated; the generated config is not verified against R7A (it sets `CONFIG_IKCONFIG_PROC=y`, unlike the observed live interface), and its recovery fstab is stale MTD/YAFFS2. A new read-only comparison found six generated partition sizes match live E2003 metadata, while the candidate userdata size differs by over 4 GiB and boot/fotakernel sizes are absent from the candidate config. This is useful cross-check evidence, not a device tree or safe image layout. No verified Android device tree, live-matched final kernel config, recovery tree, proprietary extraction recipe, or reproducible ROM product build is available. A full E2003-labelled KitKat system image is analysis material, not a source tree. Sony's open-device program covers selected Xperia models; E2003 is not listed in its current set. The 2022 no-ROM report and 2018 Oreo beta claim remain secondary/unverified and supply no reproducible ROM inputs.
- **Stock-derived FarfarRemote system image: technically plausible to build offline; device success remains unproven.** The candidate `system.sin` reconstructs as a 2,097,152,000-byte ext4 image whose `/build.prop` identifies `E2003`, API 19, Android 4.4.4, firmware `25.0.A.2.31`, and customization `1293-7276 R10A`. The phone runs `1293-7358 R7A`, so this is not a matching system image. A historical TWRP image explicitly built for E2003 has now been retrieved and statically inspected. Its kernel is byte-identical to the R10A candidate's stock kernel and its fstab maps recovery to the live p9 partition. This is substantially stronger recovery/boot-stack evidence, but its R5A customization, unaudited provenance and untested behavior on live R7A still prevent calling it a safe restore path.
- **Option C — FarfarRemote dedicated system experience: ALREADY FEASIBLE as a launcher configuration, not a ROM. VERIFIED:** the existing OS flavor registers HOME, starts FarfarRemote and retains normal Android system services, Wi-Fi settings, USB/ADB and recovery routes. Direct Android bootanimation/init/service changes require root and a matching image and are **BLOCKED** for now.

### Bootloader status correction — 2026-10-15

The conditional first-boot estimate below originally assumed the owner's
report that the bootloader was already unlocked. The subsequent Service Menu
check instead showed only `Bootloader unlock allowed: Yes`; Fastboot's
`getvar unlocked` was blank. The owner later authorized the official unlock,
and Fastboot returned `OKAY` for that command. The phone rebooted, but ADB has
not reconnected, so Service Menu confirmation of `Bootloader unlocked: Yes`
is still pending. The former 70–75% estimate remains conditional on unlock
success and image acceptance; it is not a verified end-to-end success rate.

Sony's official documentation says unlocking performs a factory reset, does
not itself grant root, and permanently removes DRM security keys that Sony
says cannot be restored. The owner later authorized the exact-device unlock;
Fastboot returned `OKAY` and the phone rebooted, but post-reset verification
of `Bootloader unlocked: Yes` is still pending because ADB has not reconnected.
Sony's current Open Devices target list does not
include E2003. That is a limitation of the current public AOSP program, not
proof that no historical Sony source archive ever existed. Sources: [Sony
unlock procedure and consequences](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader),
[Sony supported Open Devices](https://opendevices.sony.net/supported-devices-and-functionality).
No ROM image was flashed. The resulting bootloader state remains pending
Service Menu verification after Android setup and USB debugging are restored.

### FarfarOS Experimental ROM v0.1 — offline system image built, 2026-10-15

The first combined stock-derived image was built with the reproducible workflow in [`FarfarOS-v0.1/`](FarfarOS-v0.1/). It reconstructs the live R7A `/system` file state over the inspected, hash-pinned E2003 R10A ext4 container, adds the existing signed FarfarRemote OS 0.4.7 APK and integrates the owner-provided boot animation at `/system/media/bootanimation.zip`. The output is a **2,097,152,000-byte ext4 `/system` partition image** at `/tmp/FarfarOS-E2003-R7A-v0.1-system.ext4`, SHA-256 `98a7461bc9374c90016e82ce01702454b57f4c5a46795a99bfbcccd9a72e8651`. `e2fsck -fn` passed, and debugfs readback hashes matched the APK and animation inputs. Static inspection reports E2003 / Android 4.4.4 / API 19 / `25.0.A.2.31`; the APK manifest retains MAIN + HOME + DEFAULT. The image remains a local, proprietary-derived artifact and is not committed.

**This is real build progress, not a complete or flashable ROM.** No Sony SIN/FTF wrapper or validated installer was created, no exact R7A boot image was built, and the image has not been boot-tested. No ROM partition image was flashed. Package removal is intentionally zero in v0.1; hardware dependencies are preserved. See [`FarfarOS-v0.1/BUILD_REPORT.md`](FarfarOS-v0.1/BUILD_REPORT.md) for the validation gates and limitations.

## Base-version recommendation

Use stock Android 4.4.4/API 19 as the compatibility baseline now. No newer Android base is recommended until a device-specific ROM boots and passes screen/touch, Wi-Fi, audio, charging, USB/ADB, suspend/resume and Kodi tests. A 5.x/6.x MTK port is a theoretical target, not a demonstrated E2003 build. Newer OS support would require new vendor HALs/blobs, kernel compatibility, SELinux policy and working recovery; merely compiling AOSP is insufficient.

## Newly available image evidence

An unverified E2003 R10A Customized UK FTF has now yielded offline `boot`, `fotakernel` and `system` payloads. Embedded SIN SHA-256 checks passed. The reconstructed system image is the exact observed partition size; its build properties identify `1293-7276 R10A`, not the live `1293-7358 R7A`. A read-only `e2fsck` scan completes but reports an inode-bitmap padding warning, so we do not treat the filesystem check as fully clean. The boot payload includes a Linux 3.10.48+ kernel, Android init ramdisk, MediaTek fstab and Sony connectivity setup. This materially improves understanding of the stock stack and gives us a basis for offline file-level inspection. It does **not** authenticate the mirror or prove cross-CDA compatibility, provide kernel source/defconfig or device tree, or validate a restore/recovery path. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md) for file-level evidence.

### E2003 kernel source mirror candidate — 2026-10-14

The public [GitLab mirror](https://gitlab.com/sobotkama/android_kernel_sony_e2003), commit `2a84825e8268393267e454e35a00f80d48c58949`, statically contains Linux 3.10.48, MT6752 platform code, `callass` project customization, and armeabi-v7a board settings. Its claimed Sony provenance remains unauthenticated. The checked-in platform config says Linux 3.10.35 and the generated `callass` `.config` is not established as the final R7A config; notably it enables `IKCONFIG_PROC` while the live phone has no `/proc/config.gz`. The `callass` recovery fstab uses MTD/YAFFS2, conflicting with live eMMC/ext4. The kernel now **does compile offline** using Python 2.7.18, Android NDK r10e GCC 4.8 and a host compatibility flag. That proves kernel-tree buildability only; it does not establish source/config identity, Android product integration, or safe boot/recovery. Reproduce with [`tools/build_e2003_kernel_poc.sh`](tools/build_e2003_kernel_poc.sh). Details and artifact hashes: [BUILD_ENVIRONMENT.md](BUILD_ENVIRONMENT.md).

### Source and transport confidence refresh — 2026-10-15

The GitLab project README explicitly claims this kernel tree was taken from
Sony's Open Source Archive for `25.0.A.2.31` / `25.0.B.2.31`. The cited Sony
download URL currently redirects to Sony's general homepage, and the local
GitLab clone has only one grafted commit, so the source archive and tree cannot
be independently authenticated or compared at the commit-history level.
However, its `mediatek/config/callass/ProjectConfig.mk` names MT6752, a 540×960
panel, and HX8389B/C QHD panel drivers, which align with the live E2003's
platform/display properties. This improves confidence that the source tree is
for the right hardware family, while the stale MTD/YAFFS2 recovery fstab and
unmatched final kernel config remain significant boot risks.

An exact-model public search again found no reproducible E2003 Android/LineageOS
device tree or ROM. Sony's current Open Devices page also does not list E2003;
our ROM remains a stock-derived KitKat system-image experiment rather than a
supported AOSP product. The historical Oreo claim still traces to a binary-only
port described as based on a Galaxy Note 8 ROM. The currently connected handset
also entered Linux USB `0fce:adde` / `S1 Service` and returned to Android; see
[RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md). This verifies the Linux service
transport, but no image was transferred and bootloader image acceptance remains
unknown.

**Probability update (historical, conditional):** conditional first boot of
the narrow stock-derived Android 4.4 build was estimated at **about 70–75%
(low-to-moderate confidence)**, assuming the bootloader was already unlocked
and correct images could be written. The subsequent Service Menu check shows
that assumption was unsupported: only unlock eligibility is verified. The
70–75% figure must not be presented as the current end-to-end probability. It
excludes obtaining/executing the official unlock path and recovery. Exact R7A
boot parameters, boot-image acceptance, final kernel configuration and
restoration remain unresolved. No complete ROM has been boot-tested.

An attempt to reproduce the R7A `/system` POC with the retained local inputs was
stopped when host `debugfs` I/O stalled on the external workspace volume. The
partial temporary copy was removed, no output image was produced, and no phone
operation was involved. The prior successful R7A POC and its hashes above
remain the validated result; the rebuild attempt does not alter the estimate.

The extracted boot container is Sony ELF format rather than a standard Android `boot.img`. An offline tool now reconstructs a **container-format POC** using the stock kernel/ramdisk payloads and geometry from the historical E2003 recovery. This resolves the narrow header/packing question, but not whether the bootloader accepts the image, whether the R5A header geometry matches the live R7A firmware, or whether it boots. Magisk compatibility and a restore method therefore remain unverified.

### Stock-system image with FarfarRemote preinstalled — offline POC, 2026-10-14

The new [`tools/create_system_app_poc.sh`](tools/create_system_app_poc.sh) was run against the pinned-hash R10A ext4 system image and FarfarRemote OS 0.4.7 APK. It verified the APK package (`org.farfarremote`), API 19 minimum, v1 signature, and signing-certificate SHA-256 against the APK pulled read-only from the attached Xperia's existing installation. It then copied the system image outside the repository, inserted the APK at `/system/app/FarfarRemote.apk` as `root:root`, mode `0644`, and set `security.selinux=u:object_r:system_file:s0`. A byte-for-byte readback comparison passed, and `e2fsck -fn` completed with exit 0. The source image hash remained unchanged.

Output: `/mnt/data/FarfarRemote-E2003-R10A-system-preinstall-POC.img`, SHA-256 `35d8a29e1ac8b91e04c2975a832ef686166fc2d21b775669861234772fb8b731`. This is a local ext4 partition image only. It is **not** signed/repacked as a Sony SIN/FTF, does not replace the launcher or strip services, was not booted, and is not for flashing. Its base is R10A rather than live R7A. The POC verifies a repeatable offline system-image edit and app-signature continuity, but it does not reduce the main hardware boot or rollback uncertainty; the first-boot and end-to-end estimates below are unchanged.

### Stock boot-image container POC — 2026-10-14

`tools/repack_e2003_stock_boot_poc.py` assembled a local 8,445,952-byte Android legacy `boot.img` container from the extracted R10A stock kernel and stock ROOTFS ramdisk. Static checks verified that (a) the stock kernel exactly matches the retrieved E2003 recovery kernel, (b) the MediaTek ROOTFS wrapper length and gzip/newc cpio parse correctly, (c) required init files exist, and (d) output kernel and ramdisk bytes round-trip exactly. The `file` utility recognizes the result as an Android boot image with 2,048-byte pages and the recovery reference's kernel/ramdisk addresses. Output SHA-256: `1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`; it remains in private `/tmp` and is not in Git.

The reference image is an unaudited community TWRP artifact marked R5A; payloads are from an unauthenticated R10A FTF, not the phone's R7A customization. Its command line/header are borrowed from the recovery. The POC has never been booted and must not be flashed. It proves a reproducible host-side container repack only; it does **not** establish correct stock boot parameters, partition semantics, image signature acceptance, root/Magisk support, or a recovery route. Negative checks rejected a modified kernel, invalid ramdisk, and repository output path without creating an artifact. Source: [`repack_e2003_stock_boot_poc.py`](tools/repack_e2003_stock_boot_poc.py).

### Full live R7A versus candidate R10A `/system` tree comparison — 2026-10-14

The live E2003 was confirmed read-only over ADB as Android 4.4.4 / `25.0.A.2.31` / customization `1293-7358 R7A`. A full file-tree comparison against the extracted E2003 R10A candidate was run with [`tools/compare_system_trees.py`](tools/compare_system_trees.py). Counts: 4,320 R7A files, 4,283 R10A files, 4,263 common paths, 57 R7A-only and 20 R10A-only. **4,248/4,263 common paths (99.65%) are byte-identical.** Thirteen common files differ in size; fifteen differ in hash overall, meaning two additional same-size content differences. Differences include build/customization metadata, region-specific assets and Sony/Android overlays. The comparison is reproducible from captured trees; proprietary trees remain outside Git. This supersedes the earlier statement that a full pull was cancelled at ~354 MB: that statement described an earlier attempt; a later pull captured the file tree, except inaccessible `lost+found`. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).

This supports using the R10A package as a source of candidate files and confirms high userspace similarity. It is **not** proof that one complete image can replace the other: file metadata/labels, protected `lost+found`, partition layout, boot/FOTA, radio-specific state and boot behavior are not covered. The R10A `/build.prop` identifies `1293-7276 R10A`, not the installed CDA. Preserve R7A-specific files and do not wholesale replace `/system`.

### Live-matched R7A system partition POC — 2026-10-14

The attached handset was rechecked read-only and matched `E2003`, Android 4.4.4, build `25.0.A.2.31`, CDA `1293-7358 R7A`. The new [`tools/capture_e2003_system_metadata.sh`](tools/capture_e2003_system_metadata.sh) captures `/system` names, types, modes, owners, groups and SELinux labels with `ls -laRZ`; its private output is kept outside Git. [`tools/compare_e2003_system_metadata.py`](tools/compare_e2003_system_metadata.py) compared that manifest with the pinned R10A ext4 candidate. Before editing, all 4,445 common entries matched type, mode, UID, GID and symlink target; 2 live paths were missing and 2 R10A paths were extra. SELinux matched 4,443/4,445, with two R7A labels absent from R10A.

[`tools/create_r7a_system_image_poc.py`](tools/create_r7a_system_image_poc.py) then built a temporary ext4 copy using only the R7A file differences captured from the phone, removed the 17 candidate-only file/symlink paths, added 2 R7A paths, replaced 15 differing payloads, applied the two missing labels and inserted the existing signed FarfarRemote OS 0.4.7 APK. Source image SHA-256 was pinned to `931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949`; APK SHA-256 was `f412e2047daa411270d253b2e6cd8ce7097291e6deccb7e096eef3a6aab0e7bc`, with package, API 19 minimum and signing certificate checked.

The POC output SHA-256 was `3674083c9bda9171365574715d15650fda91a29658ff4ab861938cd29d838b89`. Read-only post-build checks matched all **4,447/4,447 manifest entries** for type, mode, UID, GID, SELinux label and symlink target, and SHA-256 matched all **4,193/4,193 regular-file payloads** against the live R7A pull. `e2fsck -fn` exited 0. The large generated image was removed from temporary storage after verification; no proprietary image or live metadata is in Git. Reproduce only with private local inputs, writing outside the repository:

```sh
AAPT2_BIN=/path/to/android-sdk/build-tools/35.0.0/aapt2 \
  python3 research/custom-rom/tools/create_r7a_system_image_poc.py \
  /path/to/R10A-system.ext4 /path/to/R10A-system-tree \
  /path/to/live-R7A-system-tree /path/to/private-R7A-metadata.txt \
  dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.7.apk \
  /path/outside/repository/R7A-system-poc.img
```

This is strong evidence that the **system partition contents** can be reconstructed for this R7A handset from the inspected R10A base and read-only live differences. It is still only an ext4 partition: it is not repacked as Sony SIN/FTF, has no boot chain or recovery, has not been booted, and is not flashable as delivered. It does not prove the bootloader accepts the image or provide a safe rollback path. The earlier first-boot and end-to-end success estimates therefore do not automatically increase.

### Retrieved E2003 recovery candidate — 2026-10-14

The archived XDA first post expressly identifies E2003, claims the TWRP functions were tested, and documents a recovery flash procedure. We retrieved the linked image and verified its Android boot-image header. Its embedded device/build properties identify E2003 / API 19 / `25.0.A.2.31`, and its kernel SHA-256 exactly matches the kernel segment in the R10A stock boot candidate. Its recovery fstab maps recovery to p9, which the live phone reports as `fotakernel`. The image is nevertheless a historical community artifact with customization R5A, no auditable source/build recipe or trusted checksum, and no independent test on this handset. No boot/flash/restore was attempted. It improves feasibility substantially but does not itself establish a rollback route.

The archived post and binary analysis are documented in [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md). Sony ELF-to-Android **container assembly** has a successful offline POC; hardware bootability and Magisk compatibility remain untested.

The read-only HAL/blob inventory and mismatches between the live E2003 and the mirrored `callass` config are collected in [DEVICE_TREE_BLOBS.md](DEVICE_TREE_BLOBS.md). It confirms that a private API 19 blob set can be inventoried, but no product/device tree or reproducible ROM build exists yet.

### Cross-source E2003 boot payload corroboration — 2026-10-14

A second public FTF listing identifies E2003 / `25.0.A.2.31_R3A` / branding `E2003_Customized DE_1294-2854` and publishes an AFH MD5. The complete 1.2-GB file and MD5 were not downloaded/verified; selected archive entries were fetched by byte range for offline analysis only. Its manifest plus selected ZIP CRCs and embedded SIN SHA-256 checks passed. The R3A `boot.sin` kernel and ROOTFS segments are each byte-identical to the corresponding R10A boot segments; the kernel hash also matches the historical E2003 TWRP image. This provides independent-source, same-model/same-build-family corroboration and modestly strengthens the conditional stock-first-boot assessment. It still does not identify the live R7A boot bytes or validate restore/recovery behavior. Full details and hashes: [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).

## What a minimal dedicated build must keep

Android init/Binder/system_server; SurfaceFlinger and Mali/gralloc/hwcomposer; touchscreen/input; Package Manager and text input; Wi-Fi framework, the observed `mt-wifi` driver/firmware and supplicant; network stack; storage and media path; power, battery, thermal and charging services; USB gadget and ADB; Sony/MediaTek boot and board services; and Settings or a reliable alternative path for Wi-Fi/debugging. Bluetooth can be omitted only after confirming no external controls use it. Remove user apps only after package/service dependency and recovery tests. The live stock system contains proprietary HAL/firmware artifacts, so a “minimal” image must preserve required components and respect their redistribution terms; exact dependencies are not fully mapped yet.

## Expected engineering cost and benefits

A stock-based debloat might free user RAM/storage and reduce background wake/network traffic. It does not guarantee lower idle current or faster boot: Android LMK may use free memory as cache, and vendor services may be essential. A custom OS could reduce background work, but its cost is very high because the exact device support layer is missing. Any claim of runtime/boot improvement requires repeatable measurements on this same aging battery and device.

## Required bring-up milestones for a ROM

1. Exact stock FTF, boot/FOTA images and cryptographic inventory. Current candidate is exact model/build-family but wrong CDA/revision and untrusted provenance.
2. Authenticate/validate the mirrored kernel source and derive the exact R7A final config; compare source and build IDs against the live kernel. The candidate compiles, but its current config differs from observed runtime evidence and required vendor modules are not fully mapped.
3. Device tree/BoardConfig, init/fstab, partition map and reproducible proprietary-file extraction scripts.
4. Audited E2003 recovery source/artifact and a proven non-permanent test-boot path (if the bootloader supports one).
5. Confirmed official or exact-firmware restore route plus a recoverable boot test plan.
6. First experimental image, built and inspected offline, then separately authorized device boot testing.
7. Full hardware matrix: display/touch; orientation; Wi-Fi and reboot reconnection; Bluetooth if retained; audio; storage; charging/current/thermal; USB/ADB; deep sleep/wake; Kodi app and launcher.

Until milestones 1–5 are complete, focus on the proven stock launcher and app. No image built from unrelated E4g/E4/E2033 sources is an acceptable shortcut. The current work raises confidence in **offline stock-image analysis**, not in a safe flash or successful boot.

### Read-only boot/FOTA partition access probe — 2026-10-14

The attached device was re-identified before probing as E2003 / `25.0.A.2.31`. ADB shell is UID 2000. Reading just four bytes from each of `/dev/block/platform/mtk-msdc.0/by-name/boot` and `fotakernel`, discarding the bytes to the phone's `/dev/null`, returned `Permission denied` for both. No raw data was collected or saved. [`tools/probe_e2003_boot_read_access.sh`](tools/probe_e2003_boot_read_access.sh) reproduces this bounded, read-only probe and refuses a different model/build. This confirms that ordinary ADB cannot provide the exact live boot/recovery images; recovering those bytes requires a separately verified elevated or service/recovery path. It does not prove that root or Fastboot is unavailable.

### Rejected older Android 8 ROM claim — 2026-10-14

A 2018 post titled “Install Custom ROM Sony Xperia E4g Lineage OS 15 Oreo” was reviewed. It describes a beta port based on a Samsung Galaxy Note 8 custom ROM, distributes files through redirect/file-host links, and does not identify supported E2003 customization, source tree, checksums, build logs, or independently reproducible device tests. A 2022 `/e/OS` device request explicitly says no official or unofficial LineageOS build was available at that time. The 2018 claim is therefore not accepted as proof of an E2003 Oreo port or as a source for our build. Links: [2018 ROM claim](https://dianariyanto.com/custom-rom-sony-xperia-e4g-lineage-os-15-oreo/), [/e/OS device request](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466).
