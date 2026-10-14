# E2003 device-tree and vendor-blob inventory

**Target:** Sony Xperia E4g E2003, Android 4.4.4/API 19, firmware `25.0.A.2.31`, live CDA `1293-7358 R7A`.

This is a static, private-source inventory for ROM bring-up. Proprietary system images, live device dumps, and vendor binaries remain outside Git. Nothing in this document authorizes flashing or binary redistribution.

## Evidence and status

- **VERIFIED — live identity/runtime:** read-only ADB reports product/device `E2003`, board `callass`, platform/hardware `MT6752`/`mt6752`, kernel `3.10.48+`, API 19, and CDA `1293-7358 R7A`. The sanitized input-device list includes `mtk-tpd` and `mtk-kpd`; `/proc/modules` is empty, the live `/system/lib/modules` directory is empty, and the Wi-Fi platform driver resolves to `mt-wifi`.
- **VERIFIED — captured userspace:** a private read-only R7A `/system` tree is available locally for analysis. It contains 19 files under `system/lib/hw` and 2 under `system/vendor/lib/hw`. `readelf` identifies all 21 as 32-bit ARM ELF files. Their declared `DT_NEEDED` libraries all resolve by filename somewhere in the captured `system/lib` or `system/vendor/lib` trees (zero unresolved direct dependencies in this static scan). This is not a runtime load test; `dlopen`, properties, device nodes, SELinux rules and service startup dependencies are not represented by `DT_NEEDED` alone.
- **VERIFIED — captured subsystem files:** the captured tree contains the MT6752 `gralloc` and `hwcomposer` HALs, audio and Bluetooth HALs, sensor/light/power/GPS/NFC HAL files, Bluetooth vendor HAL files, media codecs/profiles, Wi-Fi configuration and firmware files, and Sony/MediaTek permission XMLs. These are proprietary or vendor-specific inputs; their presence does not prove every feature is required or licensed for redistribution.
- **VERIFIED in the pinned mirror; not verified against the live R7A kernel:** `sobotkama/android_kernel_sony_e2003` commit `2a84825e8268393267e454e35a00f80d48c58949` has a `callass` `ProjectConfig.mk`, `fstab`, `init.project.rc`, MT6752 init configuration and MediaTek drivers. Its values include 540×960, Wi-Fi/Bluetooth/GPS enabled, NFC disabled, and touch-controller selection `ektf2k S3202`.
- **MISMATCH / UNKNOWN:** live input reports `mtk-tpd`, while the mirror's project config selects `ektf2k S3202`. The source config lists multiple candidate display-panel drivers (`hx8389b`, `hx8389c`, `hx8389c_2nd`), so the active panel is not determined by this list. The candidate `callass/init.project.rc` also requests `mtk_wmt_detect.ko`, although the captured live system has no `.ko` files in `/system/lib/modules` and the live module list is empty. That init fragment may be stale, overridden, or intended for a different packaging/configuration. Do not copy it unchanged into a product tree.
- **VERIFIED mismatch:** the mirror's `callass/recovery.fstab` is MTD/YAFFS2 and does not describe this live EMMC/ext4 handset. The separate `callass/fstab` uses `/dev/block/platform/mtk-msdc.0/by-name` for `system`, `userdata`, `cache`, `protect1` and `protect2`, and its names/filesystem types agree with the read-only live aliases/map. This fstab is a useful candidate input, not a tested mount configuration or recovery recipe.
- **UNKNOWN:** exact live R7A boot ramdisk, final kernel `.config`, selected LCD driver, complete vendor partition contents, SELinux policy changes, and which optional MTK/Sony daemons can be removed while retaining Wi-Fi reconnect, touch, charging, suspend/resume, USB/ADB and Kodi control.

## Relevant HAL files observed

The exact filenames are in the private read-only capture and are intentionally not copied into Git as binaries. The hardware-facing groups include:

- Display/composition: `gralloc.mt6752.so`, `hwcomposer.mt6752.so` and `libdisplay.default.so`.
- Input/sensors/power: `sensors.default.so`, `lights.default.so`, `power.default.so`.
- Audio/Bluetooth: `audio.primary.default.so`, `audio_policy.default.so`, `bluetooth.default.so`, plus vendor `audio.a2dp.blueangel.so` and `bluetooth.blueangel.so`.
- Other stock capabilities: `gps.default.so`, `nfc_nci_pn547.mt6752.so`, camera, keystore and MediaTek media SDK HALs.

For a Kodi remote, display/composition, touchscreen/input, Wi-Fi, power/battery/charging, storage, USB/ADB, text input and Android framework services are baseline requirements. GPS, camera and NFC are not assumed to be required, but their removal cannot be decided from filenames alone. Bluetooth remains conditional on external controls.

## Dependency and init-source audit

The static ELF dependency scan found no missing direct shared-library names among the 21 captured HAL files. The kernel mirror's two candidate init files declare 92 absolute `/system` service executables; 74 paths exist in the captured R7A `/system` tree and 18 do not. This comparison is only a cross-check of a generic source template against this product's image: conditional services, wrapper commands, symlinks, Sony init overlays and generated project files affect what actually starts. It demonstrates why the source init files must not be copied wholesale or treated as a definitive live service list.

The target `callass` config also retains phone features (modem, SIM, GPS, camera and MTK connectivity options). A dedicated build may omit a feature only after mapping its service, library, device-node and kernel dependencies and testing the resulting device behavior. The current stock launcher/app setup remains the only proven operational baseline.

## Device-tree work still needed

1. Obtain a traceable Android 4.4 product/framework source baseline and determine whether the kernel mirror's associated Android tree exists; kernel source alone cannot produce a ROM.
2. Capture or establish the exact live boot ramdisk and kernel configuration through an authorized, verified read path; ordinary shell access currently cannot read `boot` or `fotakernel`.
3. Resolve the `mtk-tpd` versus `ektf2k/S3202` input mismatch and identify the active panel driver from live kernel/device-tree evidence.
4. Build a minimal E2003 product tree (`BoardConfig.mk`, product makefiles, fstab, init overlays, properties and permissions) from verified inputs; retain proprietary binaries only in a private local blob directory with hashes and license notes.
5. Verify direct and dynamic dependencies, SELinux labels/rules, init services and hardware on a recoverable test path before removing any subsystem.

No Android product/device tree or reproducible AOSP/LineageOS product build has been produced. See [BUILD_ENVIRONMENT.md](BUILD_ENVIRONMENT.md), [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md), and [ROM_FEASIBILITY.md](ROM_FEASIBILITY.md).
