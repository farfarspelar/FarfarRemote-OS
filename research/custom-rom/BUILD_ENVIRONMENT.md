# Build environment and non-destructive tooling

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Current host snapshot

The shell/workspace used for this research reports x86_64 Linux, 4 logical CPUs, 15 GiB RAM and OpenJDK 21. After temporary source, toolchain and build outputs, `/tmp` had about 4.7 GiB free at the latest check; remove disposable `/tmp` material before attempting a full Android tree. `adb`, `fastboot`, Python 3 and Git are present; Python 2 was built locally under `/tmp` and is not installed system-wide. This shell may not be the owner's bare-metal Linux Mint host; re-run the provided checker there before choosing a build machine. The temporary `/tmp/farfar-sdk` Android SDK built both FarfarRemote APK flavors, but is not a persistent ROM toolchain.

## Feasibility

- **VERIFIED — APK:** currently works with the temporary SDK and installed Gradle wrapper.
- **BLOCKED — offline FTF/boot inspection:** feasible on this machine once a verified firmware bundle/image is obtained; current project contains no `.ftf`, `boot.img`, `recovery.img` or `system.img`.
- **UNKNOWN — Magisk source/tool build:** official Magisk build docs require Linux x64, Python 3.8+, Git, Android SDK, JDK 17 (recommended) and a downloaded ONDK via `build.py ndk`. It is not necessary to build Magisk merely to unpack a boot image. Device compatibility still needs verification.
- **BLOCKED — full modern AOSP/LineageOS:** not practical on the current workspace as configured and no E2003 device source set is available. AOSP's current guidance for recent Android lists about 400 GB free and 64 GB RAM; requirements vary by branch, but this host's 95 GB free/15 GiB RAM falls short. An old Android 4.4 build may have different requirements, yet its matching source manifest/device configuration is the larger blocker.
- **PARTIAL — kernel build:** the mirrored `callass` kernel source now generates a configuration and successfully builds an offline ARM `zImage` using a temporary Python 2.7.18 and Google's archived Android NDK r10e GCC 4.8. This proves the mirror is buildable with a legacy toolchain, not that its source provenance or generated config matches the live R7A kernel. The config enables `CONFIG_IKCONFIG_PROC=y` although live `/proc/config.gz` was absent; exact source-to-binary match remains blocked. The old kernel emits many warnings, and a modern-host `dtc` issue required `HOST_EXTRACFLAGS=-fcommon`. Details follow below.

### Device-specific kernel facts captured over read-only ADB — 2026-10-14

The live E2003 reports board `callass`, platform/hardware string `MT6752`/`mt6752`, a 32-bit ARMv7 runtime and Linux `3.10.48+` built by GCC 4.8 on 2015-09-08. The CPU MIDR part `0xd03` identifies Cortex-A53 cores. Sony specifies quad-core hardware and sysfs lists CPUs 0–3 as possible/present, but at this capture only CPU0 was online (CPUs 1–3 offline); confirm under load/cold boot before performance conclusions. CPU0 exposes MediaTek `mt-cpufreq` with `interactive` governor and 468–1495 MHz range. This narrows any eventual kernel build to the matching 32-bit Sony/MediaTek board integration; it is not evidence that a generic MT6752 tree will work. `/proc/config.gz` is absent, `/proc/cmdline` is denied to shell UID 2000, and `/proc/device-tree` is not exposed. `/system/lib/modules` is empty while Wi-Fi is bound as `mt-wifi` to platform node `180f0000.WIFI`; whether its implementation is built-in or loaded from another vendor path remains unresolved.

### E2003-specific kernel source candidate — 2026-10-14

An external [GitLab mirror](https://gitlab.com/sobotkama/android_kernel_sony_e2003), pinned at commit `2a84825e8268393267e454e35a00f80d48c58949`, describes itself as taken from Sony's archive for `25.0.A.2.31` / `25.0.B.2.31`. Static inspection of that checkout verified Linux `3.10.48`, `mediatek/config/callass`, `MTK_PLATFORM=MT6752`, `MTK_K64_SUPPORT=no`, and an `armeabi-v7a`/`armeabi` board configuration. The project files include callass-specific kernel customizations and MT6752 platform sources. These match important live E2003 facts and materially improve kernel-source availability. Sony's old archive URL now redirects to Sony's homepage; the GitLab mirror has no signed tag or independently trusted archive checksum. Treat upstream provenance as **REPORTED**, while those contents and the Git commit ID are **VERIFIED in the mirror**.

The checked-in `mediatek/config/mt6752/autoconfig/kconfig/platform` is a generated platform config labelled Linux/arm 3.10.35, with a separate `callass` project fragment. It is not yet proven to be the final `.config` used for the live R7A kernel. In particular, the fragment set includes `CONFIG_IKCONFIG_PROC=y` while live `/proc/config.gz` is absent. The callass `recovery.fstab` also describes MTD/YAFFS2, unlike the live eMMC/ext4 partition map, so it is stale for recovery planning and must not be used as a recovery recipe. This tree is kernel/platform source, not a complete Android product/device tree or restore image.

The official vendor build wrapper `./makeMtk callass n k` was run only in the temporary checkout. After building Python 2.7.18 locally (official Python source archive SHA-256 `da3080e3b488f648a3d7a4560ddee895284c3380b11d6de75edb986526b9a814`) and obtaining Google's Android NDK r10e from its official HTTPS archive (download SHA-256 `102d6723f67ff1384330d12c45854315d6452d6510286f4e5891e00a5a8f1d5a`; archive test passed), MediaTek configuration generation completed. The first compile failed for missing `arm-linux-androideabi-gcc`; the next failed because GCC 13 defaults to `-fno-common` for the legacy host `dtc`. With NDK GCC 4.8 on `PATH` and `HOST_EXTRACFLAGS=-fcommon`, the wrapper completed successfully and produced:

- ARM `zImage`: SHA-256 `640b20b8dc0e74482a9752d473f179030e48ee9efa1512968c5c374481144a45` (about 6.6 MiB).
- ARM `vmlinux`: SHA-256 `0b76a0c654fe0abfa1b2b1c75224b422e1e98d22b0f056cf28ec7fbf21430ba5` (about 161 MiB, debug symbols included).
- Reported release `3.10.48`; compiler GCC 4.8; build configuration generated for project `callass` / MT6752.

The build log contains numerous legacy warnings, including incompatible pointer types, return-type issues, and redefinitions; no warning-clean or runtime test is claimed. The generated `.config` contains `CONFIG_IKCONFIG_PROC=y`, inconsistent with the observed absence of `/proc/config.gz` on the live device. Therefore the artifact is a **kernel build proof of concept**, not a R7A-matched kernel, boot image or flashable file. Artifacts, source mirror and logs remain outside Git under `/tmp`; do not commit proprietary source or binaries or infer device compatibility from successful compilation. No phone operation occurred.

The non-destructive build wrapper is [`tools/build_e2003_kernel_poc.sh`](tools/build_e2003_kernel_poc.sh). It refuses an unexpected source commit/origin, checks for Python 2.7 and NDK GCC 4.8, and requires 3 GiB free before invoking the vendor build. Example:

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
- The root-readiness script also prints the live Sony customization fields, software-base fields, kernel string, named partition map and `/proc/partitions` sizes. It intentionally never reads raw partition contents or prints the ADB serial.
- `research/custom-rom/tools/inspect_ftf.sh`: hashes/checks/lists an FTF ZIP without extraction or flashing.
- `research/custom-rom/tools/inspect_boot_image.sh`: copies an already obtained boot image into a new output directory and invokes a user-supplied trusted host `unpack_bootimg.py`; it never writes to a device or modifies the input image.
- `research/custom-rom/tools/extract_e2003_system_image.py`: verifies SIN v3 integrity and extracts only a mapped `/system` image from an E2003/25.0.A.2.31 FTF into a new path outside Git. It uses Python standard library; `file`, `dumpe2fs`, `debugfs` and `e2fsck -fn` can inspect the resulting local image read-only. It does not extract `/data` or interact with a device.
- `research/custom-rom/tools/repack_e2003_stock_boot_poc.py`: creates an experimental Android legacy boot-image **container only** from already extracted local E2003 kernel/ramdisk payloads. It checks the recovery-reference kernel hash and ramdisk structure, refuses repository output, and has no ADB/Fastboot code. It has not produced a boot-tested image and must not be used as a flash instruction.

Do not treat checksums from an untrusted mirror as proof of authenticity. Record provenance and a cryptographic SHA-256 from an independent trusted source when possible. Never commit firmware images, proprietary blobs, private device audits or generated device dumps.
