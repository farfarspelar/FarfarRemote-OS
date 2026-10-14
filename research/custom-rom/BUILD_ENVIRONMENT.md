# Build environment and non-destructive tooling

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Current host snapshot

The shell/workspace used for this research reports x86_64 Linux, 4 logical CPUs, 15 GiB RAM, about 95 GiB free workspace storage and OpenJDK 21. `adb`, `fastboot`, Python 3 and Git are present. This shell may not be the owner's bare-metal Linux Mint host; re-run the provided checker there before choosing a build machine. The temporary `/tmp/farfar-sdk` Android SDK built both FarfarRemote APK flavors, but is not a persistent ROM toolchain.

## Feasibility

- **VERIFIED — APK:** currently works with the temporary SDK and installed Gradle wrapper.
- **BLOCKED — offline FTF/boot inspection:** feasible on this machine once a verified firmware bundle/image is obtained; current project contains no `.ftf`, `boot.img`, `recovery.img`, `system.img` or matching kernel archive.
- **UNKNOWN — Magisk source/tool build:** official Magisk build docs require Linux x64, Python 3.8+, Git, Android SDK, JDK 17 (recommended) and a downloaded ONDK via `build.py ndk`. It is not necessary to build Magisk merely to unpack a boot image. Device compatibility still needs verification.
- **BLOCKED — full modern AOSP/LineageOS:** not practical on the current workspace as configured and no E2003 device source set is available. AOSP's current guidance for recent Android lists about 400 GB free and 64 GB RAM; requirements vary by branch, but this host's 95 GB free/15 GiB RAM falls short. An old Android 4.4 build may have different requirements, yet its matching source manifest/device configuration is the larger blocker.
- **BLOCKED — kernel:** needs the exact vendor GPL source, matching defconfig/toolchain and proprietary modules. None is present locally.

References: [Magisk build instructions](https://github.com/topjohnwu/Magisk/blob/master/docs/build.md), [AOSP host requirements](https://source.android.com/docs/setup/start/requirements), [AOSP boot image tools](https://android.googlesource.com/platform/system/tools/mkbootimg/).

## Safe helper tools

- `tools/root_readiness.sh`: exact-model, read-only ADB readiness checks; does not reboot, root, unlock or write the phone.
- `research/custom-rom/tools/host_check.sh`: inventories host tools/resources only.
- The root-readiness script also prints the live Sony customization fields, software-base fields, kernel string, named partition map and `/proc/partitions` sizes. It intentionally never reads raw partition contents or prints the ADB serial.
- `research/custom-rom/tools/inspect_ftf.sh`: hashes/checks/lists an FTF ZIP without extraction or flashing.
- `research/custom-rom/tools/inspect_boot_image.sh`: copies an already obtained boot image into a new output directory and invokes a user-supplied trusted host `unpack_bootimg.py`; it never writes to a device or modifies the input image.
- `research/custom-rom/tools/extract_e2003_system_image.py`: verifies SIN v3 integrity and extracts only a mapped `/system` image from an E2003/25.0.A.2.31 FTF into a new path outside Git. It uses Python standard library; `file`, `dumpe2fs`, `debugfs` and `e2fsck -fn` can inspect the resulting local image read-only. It does not extract `/data` or interact with a device.

Do not treat checksums from an untrusted mirror as proof of authenticity. Record provenance and a cryptographic SHA-256 from an independent trusted source when possible. Never commit firmware images, proprietary blobs, private device audits or generated device dumps.
