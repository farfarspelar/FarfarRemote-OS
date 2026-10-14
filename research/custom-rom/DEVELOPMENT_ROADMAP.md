# FarfarRemote OS development roadmap

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Immediate decision

Continue the currently working Android 4.4.4 stock launcher track. Treat FarfarRemote OS today as a dedicated Android configuration, not a ROM. **REPORTED by owner, 2026-10-14:** all current FarfarRemote features have now been tested and work on both App and OS editions. **VERIFIED** in a separate physical E2003 check: the active stream folder browser opened and restored the episode directory. Keep this working software as the control baseline.

## Prioritized gates

### Gate 1 — preserve baseline and collect exact sources

- Keep the current OS APK and source commit, app preferences and a private device audit.
- Confirm model/build/customization and reported bootloader state without rebooting or modifying.
- Find official Sony/traceable E2003 25.0.A.2.31 firmware and exact matching kernel source. The E2003 R10A UK package has been archive-checked and boot/FOTA/system payloads inspected offline. The system `/build.prop` identifies `1293-7276 R10A`, not the live R7A phone, and the mirror provenance is not authenticated. It is analysis material only. The similarly named R7A Nextel-PE package is listed for E2006 and is excluded. Keep proprietary binaries out of public Git.
- **Exit:** exact firmware bundle and source/recovery provenance reviewed; restoration path documented.

### Gate 2 — offline stock image analysis (**partial progress**)

- **Done for the unverified R10A candidate only:** extracted `boot.sin`, `fotakernel.sin` and `system.sin` offline with bounds-checked readers; SIN integrity checks passed. Inspected the 3.10.48+ kernel ELF, cpio ramdisks, init scripts and fstab. Boot/FOTA share a kernel segment but have different ramdisks. Reconstructed `/system` is a 2,097,152,000-byte ext4 image; `/build.prop` confirms E2003 / 25.0.A.2.31 / API 19 / customization 1293-7276 R10A. Read-only e2fsck reports only an inode bitmap padding warning, so the filesystem is not recorded as a clean checker pass.
- Still required: obtain matching R7A images; determine whether the Sony ELF can be faithfully mapped into the correct Android boot format; inspect DTB/cmdline and kernel config. No embedded config was found and the public Sony kernel-copyleft branch search did not find an E2003/25.0.A source branch.
- Identify actual device tree/config and proprietary driver dependencies; reconcile MT6732 marketing SoC vs MT6752 platform identifiers.
- Test Magisk v22.1 boot-image parser/patch process offline on copies only, if its official legacy payload is available and trusted.
- **Exit:** reproducible parse and source/image match; no phone writes.

### Gate 3 — root feasibility decision

- Verify a stock recovery route first and ensure exact original images are accessible. A historical E4g TWRP thread and E2003 owner reports now support that a recovery was used on this family, but the artifact/build source is not auditable yet and another report describes a bootloop.
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

1. Matching stock FTF or boot/FOTA/system images with reliable provenance/hash. The E2003 R10A UK candidate passes local ZIP/SIN integrity, but has no trusted external hash and its system is `1293-7276 R10A`, not installed `1293-7358 R7A`; it is not a restore base.
2. Kernel source/defconfig/toolchain for this exact firmware and board. Candidate image reports Linux 3.10.48+ / GCC 4.8 but does not identify an exact source revision or config; no embedded config or matching Sony public branch was found.
3. E2003-specific device tree. Candidate proprietary userspace/HALs are now extractable, but match to R7A and completeness still require comparison.
4. Audited exact-variant recovery artifact and verified recovery/restore procedure; bootloader state remains owner-reported.
5. Exact device-tested root patch path; no trusted KingRoot/KingoRoot binary.
6. Unplugged controlled battery baseline and comparable post-change measurements.
7. Sufficient persistent build host/source storage for any full ROM branch.

## Probability checkpoint — 2026-10-14

To avoid conflating “can build an image” with “can safely run it on the handset,” estimates are separated by outcome. These are engineering judgments from current evidence, not statistical guarantees:

| Outcome | Current estimate | Evidence / gate |
|---|---:|---|
| Produce and inspect an offline stock-derived API 19 system-image POC from available E2003-family material | ~80% | A 2 GB ext4 system image reconstructs; 42/42 sampled essential R7A/R10A files match; toolchain can process it. Not all files are compared, and the candidate's CDA differs. |
| First boot of a modified image on this actual R7A handset | ~45–60% | Shared sampled userspace and same model/build family are favorable; actual boot/FOTA bytes, exact image match, bootloader behavior and a verified recovery path remain unknown. |
| Recover safely if that first boot fails using evidence already in hand | <30% | No exact restore package or audited recovery artifact; Sony Companion has not been shown to serve this device/build. |
| Build a newer AOSP/LineageOS ROM for E2003 | <20% | Exact kernel source/config and device tree are still absent; no reproducible port was found. |

The requested ≥70% confidence has been reached only for the limited **offline stock-derived image-analysis/assembly** milestone. It has **not** been reached for a modified image successfully booting, being fully usable, or being recoverable on the phone. Raising those claims without the missing evidence would be misleading. The highest-value next step is to establish an exact restore route and audit the historical E2003 recovery source/artifact, then compare boot/FOTA payloads if the owner deliberately places the phone into an appropriate read-only diagnostic mode. No fastboot transition or device write has been performed.

**Root research note:** a 2016 community report describes KingRoot on E2003/Android 4.4.4/build `25.0.A.2.31`, but the handset had previously been rooted and commenters questioned whether residual files explain the result. Treat it as weak evidence only; APK/version/provenance, CDA and reproducibility are missing. It is not an approved procedure. See [ROOT_METHODS.md](ROOT_METHODS.md).
