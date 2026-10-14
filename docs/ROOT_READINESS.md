# E2003 Root and FarfarRemote OS Readiness

## What FarfarRemote OS means today

The existing `org.farfarremote` OS flavor is a dedicated-use configuration of Android: it shares the remote-control code with the App flavor, registers as a HOME activity, and uses the full-screen remote UI. It is not a replacement Android ROM. This is already enough to make the E2003 a dedicated Kodi controller while retaining Sony's working display, touch, Wi-Fi, power and USB-debugging support.

Root is only needed for deeper system-level work such as changing `/system`, removing protected system packages, replacing boot assets or building a custom system image. Those are separate from implementing the FarfarRemote launcher OS and carry substantially more recovery risk.

## Current read-only device findings — 2026-10-14

The connected ADB device reports:

- Model and device: `E2003`
- Firmware: `25.0.A.2.31`
- Sony customization: `1293-7358`, revision `R7A`
- Android: `4.4.4`, API 19
- Build fingerprint: `Sony/E2003/E2003:4.4.4/25.0.A.2.31/4Pf_Nw:user/release-keys`
- CPU ABI: `armeabi-v7a` / `armeabi`; CPU reports ARMv7
- Kernel: `3.10.48+`, built 2015-09-08
- Android build flags: `user`, `release-keys`, `ro.secure=1`, `ro.debuggable=0`
- `ro.hardware` and `/proc/cpuinfo` identify the MT6752 family string. Public E4g descriptions also call the single-SIM E2003 MT6732. Treat these strings as an unresolved vendor naming/platform detail; they do not make another MT67xx phone's boot or recovery image compatible.
- ADB shell identity: UID 2000 (`shell`), SELinux context `u:r:shell:s0`
- Root through the current ADB shell: unavailable
- `su` command on the Android shell's PATH: absent
- Packages already reported disabled by Android: `com.sonyericsson.startupflagservice` and `com.sonymobile.usm`

Those two packages were already disabled when this read-only check ran. This work did not disable or re-enable them, and their prior state does not establish whether root was used to disable them.

The read-only partition map exposes labels including `boot`, `fotakernel`, `system`, `userdata`, `cache`, `lk`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1`, `tee2`, and `ta`. `/system` is mounted read-only. This is enough to identify names that must be protected, but not enough to make raw partition copies from this unrooted ADB session. **Never write to `ta`, `nvram`, `proinfo`, `protect1/2`, `secro`, `tee1/2`, or `seccfg` as part of a FarfarRemote ROM experiment.** No raw partition contents were read.

The kernel-reported partition sizes (1 KiB blocks) include `boot` (`mmcblk0p10`, 32,768 blocks), `fotakernel` (`p9`, 32,768), `system` (`p19`, 2,048,000), `cache` (`p20`, 204,800), and `userdata` (`p21`, 5,168,640). Protected examples include `ta` (`p1`), `nvram` (`p3`), `protect1/2` (`p4/p5`), `secro` (`p11`) and `tee1/2` (`p15/p16`). These are device-reported labels/sizes, not instructions to access or flash them. The bootloader's accepted image formats and partition write behavior are still unknown.

The workstation currently has Linux Mint 22.3 x86_64, 4 logical CPUs, about 15 GiB RAM and 95 GiB free on the workspace volume. It has ADB and Fastboot; Heimdall is also installed but is a Samsung-oriented flasher and is not an E2003 restore solution. Sony Flashtool, SP Flash Tool, `repo`, kernel unpack/pack utilities and Android source build prerequisites are not installed. A temporary Android SDK at `/tmp/farfar-sdk` was used to build both FarfarRemote APK flavors successfully on 2026-10-14. That proves APK builds are available in the current session, not that this temporary SDK is a persistent ROM build environment.

The project owner reports that the bootloader is unlocked. Earlier read-only fastboot queries did not independently confirm the unlock state: `getvar unlocked` returned no value and this bootloader did not support `oem device-info`. An unlocked bootloader does not make the running Android shell root.

Run `tools/root_readiness.sh` from Linux Mint when the phone is in normal Android/ADB mode. It checks the exact model and firmware, current shell UID, whether `su` is on the Android shell's PATH, package-disable state, and fastboot properties only if the phone is already in fastboot mode. It does not reboot the phone, invoke `su`, change settings, unlock, flash or write partitions. It intentionally omits USB serial numbers from its report.

## Root and recovery leads

There is a historical user report claiming KingRoot obtained root on an **E2003 running `25.0.A.2.31`**, and another report says bootloader unlock, KingRoot and TWRP were used on an E4g. This is useful evidence that root may be possible, but not a reproducible or trusted method: the report does not provide an auditable binary/hash, verified download provenance, clean-room behavior, exact customization-code match, or a tested restore procedure. Treat the APK and its network behavior as untrusted until independently vetted. [Historical exact-firmware report](https://4pda.to/forum/index.php?showtopic=668811&st=360), [later E2003/TWRP report](https://4pda.to/forum/index.php?showtopic=668811&st=480).

An unofficial 2017 article offers E4g TWRP ZIPs, while older forum discussions mention TWRP for E4g and note boot-image unpacking issues. The available claims do not establish whether a particular artifact is for E2003 single-SIM versus E2033/E2043 dual-SIM, which bootloader/firmware it supports, or whether the download is intact. No recovery artifact has been downloaded or tested. [Unofficial E4g TWRP instructions](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/), [historical recovery discussion](https://forum.android.com.pl/topic/234990-xperia-e4g-e2003-e2006-e2053-w%C4%85tek-zbiorowy/285).

No verified recovery image, patched boot image or source tree for this exact E2003/firmware/customization combination is present in the repository. The repository also contains no stock `.ftf`, `boot.img`, `recovery.img`, or system image. Do not substitute E2033 dual-SIM or other Xperia/MT6732 artifacts.

Public source search found a Sony MT6752 kernel repository identified for Xperia C4/C5 Ultra, but no E2003 device tree in that repository. Shared kernel-family source alone is not a compatible E2003 kernel/configuration. A 2019 community post says someone had downloaded sources and was assembling a device tree, but no verified published E2003 build was found. The /e/OS community reported no official or unofficial LineageOS build for E2003 in 2022 and flagged a purported Oreo port as possibly fake. [Sony MT6752 kernel repository](https://github.com/sony-mt6752/android_kernel_sony_mt6752-common), [E2003 ROM support discussion](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466). Sony's AOSP kernel-build guide lists selected supported devices such as Xperia E3, but not E4g/E2003. [Sony 32-bit kernel guide](https://developer.sony.com/open-source/aosp-on-xperia-open-devices/guides/kernel-compilation-guides/how-to-build-and-flash-a-linux-kernel-for-aosp-supported-devices/how-to-manually-build-the-linux-kernel-for-32-bit-devices).

An exact-model/firmware stock bundle is listed on Android File Host (`E2003_25.0.A.2.31_R3A_E2003_Customized DE_1294-2854.ftf`, 1.2 GB), but it is a 2017 user upload, its listed checksum is MD5, and its customization differs from the connected phone's `1293-7358 R7A`. A second community listing names `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` (1.2 GB), with a Google Drive link but no published cryptographic checksum or independently established relation to CDA `1293-7358 R7A`. These are leads for offline inspection only, **not verified restore packages**. The exact region/customization bundle or a documented cross-customization restore plan still needs to be sourced and independently checked. [Android File Host listing](https://androidfilehost.com/?flid=212192&w=files), [community firmware index](https://azrom.net/rom-sony-xperia-e4g-e2003-e2006-e2053-ftf-firmware-lock-remove-file/).

## Implementation decision

Continue FarfarRemote OS on the stock Sony system for now. The current project already implements the dedicated launcher path; recent OS work has added OS-only battery controls without changing the App flavor. A custom ROM is not ready to build: the exact E2003 board configuration, matching kernel source/toolchain, proprietary vendor components, partition map and reproducible image build have not been collected and verified together.

The next safe root-readiness work, before any on-device mutation, is:

1. Preserve the current app/configuration and capture a fresh, private device audit.
2. Locate the Sony GPL source archive matching E2003 `25.0.A.2.31` and `1293-7358 R7A`; verify its contents include the matching kernel and board configuration. The archive was not found in the current project or official Open Devices source tree search.
3. Obtain the exact regional stock firmware from a trustworthy source, verify its published hashes/signatures where available, and keep it outside public Git if redistribution rights are unclear. The AFH file is only a candidate because its region differs and its published hash is MD5.
4. Recover/extract the matching boot image, ramdisk, fstab, init scripts, kernel config and vendor blobs offline; establish boot image header/offsets and exact partition sizes without writing to the phone.
5. Verify a Linux flash/restore workflow can identify this exact E2003 and restore the stock FTF in a dry-run/offline review. Install and test the tooling separately; do not start a write operation.
6. Check the historical root APK and E4g recovery packages for provenance, exact model/firmware, hashes, signatures and reproducible behavior. If that evidence cannot be established, do not use them.
7. Only after a concrete, verified method and restore path exist, decide whether to proceed with a narrowly scoped root attempt. Root, package removal, reboot-to-bootloader, and partition writes are separate device operations; this readiness work has not performed them.

## Minimum ROM contents for FarfarRemote

The smallest sensible target is a **stock-based Android 4.4.4 image** retaining Sony's matching kernel, board/HAL binaries and boot configuration, while removing only explicitly selected user-space apps after dependency testing. At minimum, keep Android init, Binder/system_server, SurfaceFlinger/gralloc/display, touchscreen/input, Package Manager/installer, Settings/input method, Wi-Fi framework + vendor driver/firmware, network stack, power/charging/thermal services, storage, USB/ADB and the Sony-specific power service. Bluetooth can be optional if its full firmware/HAL path is retained and tested. FarfarRemote then remains a normal app/HOME launcher. A clean AOSP or modern LineageOS port would additionally need a supported base branch, full E2003 device/vendor trees, kernel config/source, proprietary blobs and sustained hardware bring-up; none is currently verified.

## Workstation fit

This workstation is sufficient for APK work and likely suitable for offline image inspection, but has only 95 GiB free and 15 GiB RAM. Google's current AOSP requirements for Android 9+ list 400 GB free storage and 64 GB RAM; those numbers do not directly describe a KitKat/stock-image build, but they show this machine cannot reasonably host a current full AOSP tree/build. Any later full ROM build should use a larger Linux build host. [AOSP build requirements](https://source.android.com/docs/setup/start/requirements).

If these prerequisites cannot be met, retain the stock-based OS flavor and optimize only through app behavior and reversible Android settings. The earlier attempt to disable packages was rejected by this firmware, so root should not be treated as an assumption in debloat scripts.

## Evidence and limits

- Live ADB checks are read-only and describe the connected device at the time of capture. They do not prove bootloader state or guarantee a battery, network or recovery condition.
- The owner's report is the evidence that the bootloader is unlocked; independent confirmation remains unavailable through the current fastboot commands.
- Historical community root claims are leads for research, not verified instructions or endorsement.
- Sony's official bootloader guidance explains that unlocking is distinct from obtaining root and may have device/data consequences: [Sony Open Devices bootloader guide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader/).
- The historical E4g firmware discussion includes E2003 and E2033 firmware information and user-generated root claims; it is not a verified security/recovery source: [4PDA Xperia E4g firmware thread](https://4pda.to/forum/index.php?showtopic=668811).
- Sony's user guide identifies the E2003/E2006/E2053 Android 4.4.4 family: [Sony Xperia E4g user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf).
