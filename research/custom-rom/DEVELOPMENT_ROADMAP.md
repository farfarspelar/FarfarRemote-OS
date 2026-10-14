# FarfarRemote OS development roadmap

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Immediate decision

Continue the currently working Android 4.4.4 stock launcher track. Treat FarfarRemote OS today as a dedicated Android configuration, not a ROM. **REPORTED** by owner: Kodi controls, Find My Kodi, favorites, Kodi-host Power Off, Wi-Fi reconnect after reboot, HOME launcher and Android timeout work on-device. **VERIFIED** in a separate physical E2003 check: the active stream folder browser opened and restored the episode directory. Keep this working software as the control baseline.

## Prioritized gates

### Gate 1 — preserve baseline and collect exact sources

- Keep the current OS APK and source commit, app preferences and a private device audit.
- Confirm model/build/customization and reported bootloader state without rebooting or modifying.
- Find official Sony/traceable E2003 25.0.A.2.31 firmware and exact matching kernel source. Record SHA-256 and licensing/provenance; keep proprietary binaries out of public Git.
- **Exit:** exact firmware bundle and source/recovery provenance reviewed; restoration path documented.

### Gate 2 — offline stock image analysis

- Extract a copy of E2003 boot/FOTA/system images with versioned tools.
- Inspect boot header, kernel, ramdisk, init/fstab, DTB/cmdline, compression and image size.
- Identify actual device tree/config and proprietary driver dependencies; reconcile MT6732 marketing SoC vs MT6752 platform identifiers.
- Test Magisk v22.1 boot-image parser/patch process offline on copies only, if its official legacy payload is available and trusted.
- **Exit:** reproducible parse and source/image match; no phone writes.

### Gate 3 — root feasibility decision

- Verify a stock recovery route first and ensure exact original images are accessible.
- Compare a controlled historical Magisk boot patch vs retaining unrooted Android. Do not run opaque KingRoot/KingoRoot tools.
- Obtain separate authorization before on-device root/bootloader operation.
- **Exit:** only if recovery works and expected data loss/risk is understood; verify root read-only before any package change.

### Gate 4 — measured stock optimization

- Capture matched battery baselines (screen off/on, Kodi idle/playback/offline, intermittent use) unplugged.
- Apply one reversible app/system setting at a time; test Wi-Fi reconnect after sleep/reboot and every Kodi control.
- Compare real elapsed/percentage and batterystats; no 24-hour claim without repeated results.
- **Exit:** demonstrable repeatable gain with no usability regression.

### Gate 5 — custom stock-based image proof of concept

- Only after exact source + images + recovery route: create a local, clearly experimental ramdisk/system image or minimal stock-based image. Preserve vendor display/touch/Wi-Fi/power/charging/USB components.
- Build and inspect offline first. Boot testing requires explicit authorization and a rollback plan.
- **Exit:** boots and passes hardware matrix, not merely successful compilation.

### Gate 6 — newer Android ROM evaluation

- Begin only if complete E2003 device/vendor/kernel trees or a maintainable upstream port emerge. Start from the newest branch compatible with 32-bit kernel/vendor HALs; do not select an Android version based on Magisk availability alone.
- No source support currently establishes a realistic newer base. Android 5.1 or 6.0 is only a research question, not a recommendation.
- **Exit:** device tree, kernel, blobs, recovery and hardware tests exist before proposing replacement of KitKat.

## Exact blockers now

1. Matching stock FTF or boot/FOTA image with reliable provenance/hash.
2. Kernel source/defconfig/toolchain for this exact firmware and board.
3. E2003-specific device tree and complete compatible vendor blobs.
4. Verified recovery/restore procedure and bootloader state.
5. Exact device-tested root patch path; no trusted KingRoot/KingoRoot binary.
6. Unplugged controlled battery baseline and comparable post-change measurements.
7. Sufficient persistent build host/source storage for any full ROM branch.
