# Build environment and non-destructive tooling

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Current host snapshot

**Rechecked 2026-10-14:** this shell reports x86_64 Linux, 4 logical CPUs, 15 GiB RAM and OpenJDK 21. The repository workspace is on `/mnt/data` with 93 GiB free, but `/tmp` shares the nearly full system volume and has only 4.7 GiB free. Do not put ROM source/output under `/tmp`; use the workspace volume or a dedicated larger build disk. `adb`, `fastboot`, Python 3 and Git are present. `repo`, `ndk-build`, `emulator` and `lunch` are not on `PATH`; the kernel POC's legacy Python 2.7 and NDK r10e exist only under temporary locations. AOSP source and build requirements vary by branch; this host is below current AOSP guidance and 93 GiB is a tight/possibly insufficient budget for a complete old Android checkout plus outputs. More importantly, no E2003 Android product/device tree is available yet. The temporary `/tmp/farfar-sdk` Android SDK built both FarfarRemote APK flavors, but is not a persistent ROM toolchain.

## Feasibility

- **VERIFIED — APK:** currently works with the temporary SDK and installed Gradle wrapper.
- **BLOCKED — offline FTF/boot inspection:** feasible on this machine once a verified firmware bundle/image is obtained; current project contains no `.ftf`, `boot.img`, `recovery.img` or `system.img`.
- **UNKNOWN — Magisk source/tool build:** official Magisk build docs require Linux x64, Python 3.8+, Git, Android SDK, JDK 17 (recommended) and a downloaded ONDK via `build.py ndk`. It is not necessary to build Magisk merely to unpack a boot image. Device compatibility still needs verification.
- **BLOCKED — full modern AOSP/LineageOS:** not practical on the current workspace as configured and no E2003 device source set is available. AOSP's current guidance for recent Android lists about 400 GB free and 64 GB RAM; requirements vary by branch, but this host's 95 GB free/15 GiB RAM falls short. An old Android 4.4 build may have different requirements, yet its matching source manifest/device configuration is the larger blocker.
- **PARTIAL — kernel build:** the mirrored `callass` kernel source now generates a configuration and successfully builds an offline ARM `zImage` using a temporary Python 2.7.18 and Google's archived Android NDK r10e GCC 4.8. This proves the mirror is buildable with a legacy toolchain, not that its source provenance or generated config matches the live R7A kernel. The config enables `CONFIG_IKCONFIG_PROC=y` although live `/proc/config.gz` was absent; exact source-to-binary match remains blocked. The old kernel emits many warnings, and a modern-host `dtc` issue required `HOST_EXTRACFLAGS=-fcommon`. Details follow below.
- **VERIFIED — stock system image edit POC:** [`tools/create_system_app_poc.sh`](tools/create_system_app_poc.sh) inserts the existing API 19 FarfarRemote OS APK into a copy of the locally inspected R10A ext4 image. It pins the source image hash and APK signing certificate, applies the expected SELinux file label, validates a readback, and runs `e2fsck -fn`. It requires `debugfs`, `e2fsck`, `file`, `keytool`, `jarsigner`, `cmp`, and Android SDK `aapt2` (`AAPT2_BIN`). Example (use a destination outside Git):

  ```sh
  AAPT2_BIN="$ANDROID_HOME/build-tools/35.0.0/aapt2" research/custom-rom/tools/create_system_app_poc.sh /path/to/verified-local-R10A-system.ext4 dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.7.apk /path/outside/repository/FarfarRemote-system-poc.img
  ```

  The current run produced SHA-256 `35d8a29e1ac8b91e04c2975a832ef686166fc2d21b775669861234772fb8b731` and passed ext4 checking. This is an offline filesystem-image POC, not a complete firmware package, not boot-tested and not suitable to flash.

- **VERIFIED — live-R7A system image reconstruction POC:** [`tools/capture_e2003_system_metadata.sh`](tools/capture_e2003_system_metadata.sh), [`tools/compare_e2003_system_metadata.py`](tools/compare_e2003_system_metadata.py), and [`tools/create_r7a_system_image_poc.py`](tools/create_r7a_system_image_poc.py) reproduce the private offline workflow. With a read-only E2003 R7A `/system` tree + manifest, the pinned R10A ext4 source, and the signed OS APK, the script generated a R7A-derived ext4 copy. Post-build verification matched **4,447/4,447** entries for type/mode/UID/GID/SELinux/symlink target and **4,193/4,193** regular-file SHA-256 payloads against the captured live tree; `e2fsck -fn` returned 0. Output hash: `3674083c9bda9171365574715d15650fda91a29658ff4ab861938cd29d838b89`. The image was deleted after validation and is not distributed. Python 3.9+, e2fsprogs (`debugfs`, `e2fsck`), `aapt2`, `keytool`, and `jarsigner` are needed. The scripts refuse repository output and never write to ADB/Fastboot. This validates a system filesystem reconstruction only, not SONY SIN packaging, boot acceptance, recovery or device boot.

### Device-specific kernel facts captured over read-only ADB — 2026-10-14

The live E2003 reports board `callass`, platform/hardware string `MT6752`/`mt6752`, a 32-bit ARMv7 runtime and Linux `3.10.48+` built by GCC 4.8 on 2015-09-08. The CPU MIDR part `0xd03` identifies Cortex-A53 cores. Sony specifies quad-core hardware and sysfs lists CPUs 0–3 as possible/present, but at the latest capture only CPU0 was online (CPUs 1–3 offline); confirm under load/cold boot before performance conclusions. CPU0 exposes MediaTek `mt-cpufreq` with `interactive` governor and 468–1495 MHz range. This narrows any eventual kernel build to the matching 32-bit Sony/MediaTek board integration; it is not evidence that a generic MT6752 tree will work. `/proc/config.gz` is absent, `/proc/cmdline` is denied to shell UID 2000, and `/proc/device-tree` is not exposed. A fresh read-only capture also found `wlan0` bound to `mt-wifi` at `180f0000.WIFI`, no entries in `/proc/modules`, no module files in `/system/lib/modules` or standard vendor module paths, and MediaTek Wi-Fi firmware/configuration files in `/system/etc/firmware`. The pattern is consistent with a built-in vendor driver but is not conclusive; retain the stock kernel/firmware pairing until verified. Detailed observations are in [DEVICE_HARDWARE.md](DEVICE_HARDWARE.md).

### Candidate callass partition-size cross-check — 2026-10-14

The generated `BoardConfig.mk` and `partition_size.mk` in the pinned, unverified kernel-source mirror were compared with a fresh read-only ADB capture using [`tools/compare_partition_config.py`](tools/compare_partition_config.py). The candidate values match live raw partition sizes for `system` (2,097,152,000 bytes), `cache` (209,715,200), `protect1` and `protect2` (10,485,760 each), `ltalabel` (16,777,216), and `secro` (6,291,456). The live `boot` p10 and `fotakernel` p9 partitions are each 33,554,432 bytes; the generated makefiles do not declare corresponding `*_IMAGE_PARTITION_SIZE` values. **One discrepancy needs explanation:** candidate `BOARD_USERDATAIMAGE_PARTITION_SIZE` is 1,237,319,680 bytes, while live `userdata` p21 is 5,292,687,360 bytes. This may represent a smaller build-time userdata image rather than the physical partition extent, but that interpretation is **UNKNOWN**. Do not copy the generated sizing blindly into a new product configuration until its MediaTek build semantics are verified. This check improves partition-map confidence but does not authenticate the kernel source or make a flashable ROM.

Re-run the offline comparison with a fresh, private capture and the candidate makefiles (the capture can contain device-specific details; keep it out of Git):

```sh
research/custom-rom/tools/collect_e2003_prerequisites.sh > /path/outside/repository/e2003-prerequisites.txt
python3 research/custom-rom/tools/compare_partition_config.py \
  /path/outside/repository/e2003-prerequisites.txt \
  /path/to/kernel-source/out/target/product/callass/obj/CUSTGEN/config/BoardConfig.mk \
  /path/to/kernel-source/out/target/product/callass/obj/PTGEN/configs/partition_size.mk
```

The collector requires an attached, authorized E2003 ADB target. Exit 0 means all candidate sizes were matched; exit 1 means one or more mismatches; exit 3 means some candidate values could not be mapped; exit 2 means the input format or files were invalid. The helper reads the capture and makefiles only and does not contact the device.

### E2003-specific kernel source candidate — 2026-10-14

An external [GitLab mirror](https://gitlab.com/sobotkama/android_kernel_sony_e2003), pinned at commit `2a84825e8268393267e454e35a00f80d48c58949`, describes itself as taken from Sony's archive for `25.0.A.2.31` / `25.0.B.2.31`. Static inspection of that checkout verified Linux `3.10.48`, `mediatek/config/callass`, `MTK_PLATFORM=MT6752`, `MTK_K64_SUPPORT=no`, and an `armeabi-v7a`/`armeabi` board configuration. The project files include callass-specific kernel customizations and MT6752 platform sources. These match important live E2003 facts and materially improve kernel-source availability. Sony's old archive URL now redirects to Sony's homepage; the GitLab mirror has no signed tag or independently trusted archive checksum. Treat upstream provenance as **REPORTED**, while those contents and the Git commit ID are **VERIFIED in the mirror**.

The checked-in `mediatek/config/mt6752/autoconfig/kconfig/platform` is a generated platform config labelled Linux/arm 3.10.35, with a separate `callass` project fragment. It is not yet proven to be the final `.config` used for the live R7A kernel. In particular, the fragment set includes `CONFIG_IKCONFIG_PROC=y` while live `/proc/config.gz` is absent. The callass `recovery.fstab` also describes MTD/YAFFS2, unlike the live eMMC/ext4 partition map, so it is stale for recovery planning and must not be used as a recovery recipe. This tree is kernel/platform source, not a complete Android product/device tree or restore image.

The official vendor build wrapper `./makeMtk callass n k` was run only in the temporary checkout. After building Python 2.7.18 locally (official Python source archive SHA-256 `da3080e3b488f648a3d7a4560ddee895284c3380b11d6de75edb986526b9a814`) and obtaining Google's Android NDK r10e from its official HTTPS archive (download SHA-256 `102d6723f67ff1384330d12c45854315d6452d6510286f4e5891e00a5a8f1d5a`; archive test passed), MediaTek configuration generation completed. The first compile failed for missing `arm-linux-androideabi-gcc`; the next failed because GCC 13 defaults to `-fno-common` for the legacy host `dtc`. With NDK GCC 4.8 on `PATH` and `HOST_EXTRACFLAGS=-fcommon`, the wrapper completed successfully and produced:

- ARM `zImage`: SHA-256 `640b20b8dc0e74482a9752d473f179030e48ee9efa1512968c5c374481144a45` (about 6.6 MiB).
- ARM `vmlinux`: SHA-256 `0b76a0c654fe0abfa1b2b1c75224b422e1e98d22b0f056cf28ec7fbf21430ba5` (about 161 MiB, debug symbols included).
- Reported release `3.10.48`; compiler GCC 4.8; build configuration generated for project `callass` / MT6752.

The build log contains numerous legacy warnings, including incompatible pointer types, return-type issues, and redefinitions; no warning-clean or runtime test is claimed. The generated `.config` contains `CONFIG_IKCONFIG_PROC=y`, inconsistent with the observed absence of `/proc/config.gz` on the live device. Therefore the artifact is a **kernel build proof of concept**, not a R7A-matched kernel, boot image or flashable file. Artifacts, source mirror and logs remain outside Git under `/tmp`; do not commit proprietary source or binaries or infer device compatibility from successful compilation. No phone operation occurred.

The non-destructive build wrapper is [`tools/build_e2003_kernel_poc.sh`](tools/build_e2003_kernel_poc.sh). It refuses an unexpected source commit/origin, checks for Python 2.7 and NDK GCC 4.8, and requires 3 GiB free before invoking the vendor build. The host inventory helper now reports both the workspace and `/tmp` filesystems and checks for common Android build tools (`repo`, `ndk-build`, `emulator`, `lunch`) so a nearly full root volume is visible before starting a large build. Example:

```sh
research/custom-rom/tools/build_e2003_kernel_poc.sh \
  /path/to/android_kernel_sony_e2003 \
  /path/to/android-ndk-r10e \
  /path/to/python2.7
```

References: [Magisk build instructions](https://github.com/topjohnwu/Magisk/blob/master/docs/build.md), [AOSP host requirements](https://source.android.com/docs/setup/start/requirements), [AOSP boot image tools](https://android.googlesource.com/platform/system/tools/mkbootimg/).

## Safe helper tools

- `tools/root_readiness.sh`: exact-model, read-only ADB readiness checks; does not reboot, root, unlock or write the phone.
- `research/custom-rom/tools/collect_e2003_prerequisites.sh`: verifies exactly one authorized E2003 running build ID `25.0.A.2.31`, then prints device/kernel/CPU-frequency/partition metadata, Wi-Fi driver bindings, display density, available hardware HAL filenames and sanitized input-device names/handlers. It does not print the ADB serial, save a report, read raw partition contents, or reboot/write the phone.
- `research/custom-rom/tools/host_check.sh`: inventories host tools/resources only.
- `research/custom-rom/tools/compare_partition_config.py`: offline size comparison between candidate MediaTek makefile partition values and a read-only prerequisite capture; reports mismatches without accessing a device.
- `research/custom-rom/tools/read_e2003_boot_partitions_mtkclient.sh`: pinned, bounded read-only wrapper for exact live `boot` and `fotakernel` dumps through MTKClient. It is prepared but not yet run in BootROM mode; see [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md) for its scope and risk.
- The root-readiness script also prints the live Sony customization fields, software-base fields, kernel string, named partition map and `/proc/partitions` sizes. It intentionally never reads raw partition contents or prints the ADB serial.
- `research/custom-rom/tools/inspect_ftf.sh`: hashes/checks/lists an FTF ZIP without extraction or flashing.
- `research/custom-rom/tools/inspect_boot_image.sh`: copies an already obtained boot image into a new output directory and invokes a user-supplied trusted host `unpack_bootimg.py`; it never writes to a device or modifies the input image.
- `research/custom-rom/tools/extract_e2003_system_image.py`: verifies SIN v3 integrity and extracts only a mapped `/system` image from an E2003/25.0.A.2.31 FTF into a new path outside Git. It uses Python standard library; `file`, `dumpe2fs`, `debugfs` and `e2fsck -fn` can inspect the resulting local image read-only. It does not extract `/data` or interact with a device.
- `research/custom-rom/tools/repack_e2003_stock_boot_poc.py`: creates an experimental Android legacy boot-image **container only** from already extracted local E2003 kernel/ramdisk payloads. It checks the recovery-reference kernel hash and ramdisk structure, refuses repository output, and has no ADB/Fastboot code. It has not produced a boot-tested image and must not be used as a flash instruction.

Do not treat checksums from an untrusted mirror as proof of authenticity. Record provenance and a cryptographic SHA-256 from an independent trusted source when possible. Never commit firmware images, proprietary blobs, private device audits or generated device dumps.
