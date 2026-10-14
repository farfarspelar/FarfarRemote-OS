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
- New evidence: a complete captured R7A/R10A `/system` comparison shows 4,248/4,263 common paths byte-identical. A newly completed R3A candidate comparison shows 4,247/4,258 common paths byte-identical (99.74%); the full R3A FTF MD5 matches the AFH listing and its ZIP test passes. Both alternate CDAs remain non-restoration evidence. A retrieved historical E2003 TWRP candidate has the exact same kernel bytes as the R10A candidate and fstab maps p9 to recovery, matching the live `fotakernel` partition number. An offline repack tool assembles and validates a legacy boot-image container from Sony ELF payloads, but its boot metadata is not device-validated. Still required: R7A-matched inputs, valid stock boot parameters/DTB requirements and a device boot test. No embedded kernel config or matching public kernel branch found.
- **Offline boot-container POC built:** `/tmp/farfar-e2003-r3a-stock-boot-poc.img`, 8,445,952 bytes, SHA-256 `1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`. Host `file` recognizes the legacy Android boot-image header; the builder round-tripped both payloads and the image is below p9's observed 32 MiB size. It combines E2003-family stock kernel/ROOTFS bytes with geometry from an unaudited R5A TWRP image. This validates a container assembly path only; it is not R7A-matched, boot-tested, a ROM, or suitable for flashing. The artifact remains outside Git.
- Identify actual device tree/config and proprietary driver dependencies; reconcile MT6732 marketing SoC vs MT6752 platform identifiers.
- Test Magisk v22.1 boot-image parser/patch process offline on copies only, if its official legacy payload is available and trusted.
- **Exit:** reproducible parse and source/image match; no phone writes.

### Gate 3 — root feasibility decision

- A historical E2003 TWRP 2.8.7.0 artifact is now retrievable and statically parsed. Its kernel matches the E2003 R10A boot kernel byte-for-byte, and its recovery fstab uses p9. But the build has no source recipe/checksum, is customized R5A, and has not been tested on live R7A. Validate exact stock restoration first; no image load/write yet.
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

1. Exact/official recovery base for live CDA `1293-7358 R7A`; available R10A and R3A community candidates have internally verified ZIP/SIN data but no trusted Sony provenance and their customization IDs differ from the handset.
2. Kernel source/defconfig/toolchain for this exact firmware and board. Candidate image reports Linux 3.10.48+ / GCC 4.8 but does not identify an exact source revision or config; no embedded config or matching Sony public branch was found.
3. E2003-specific device tree. Candidate proprietary userspace/HALs are now extractable, but match to R7A and completeness still require comparison.
4. Recovery operation and restore procedure remain unverified. A historical E2003 TWRP candidate is a strong lead (matching kernel and p9 mapping) but is R5A, unaudited and untested on R7A; unlock state remains owner-reported.
5. Exact device-tested root patch path; no trusted KingRoot/KingoRoot binary.
6. Unplugged controlled battery baseline and comparable post-change measurements.
7. Sufficient persistent build host/source storage for any full ROM branch.

### New tooling evidence — 2026-10-14

The public Flashtool device database was inspected at a pinned commit. Its `E20XX` profile explicitly recognizes E2003 and provides the Sony Flashmode FTF workflow; this makes Flashtool a credible host-side restore-tool candidate **if** an exact, verified FTF is found. Its generic profile does not bundle a recovery bootkit, and its FSC recipe includes sensitive partitions, so the profile is not itself a safe rollback plan. Sony's general Companion matrix lists Software Repair for all Xperia products and the E4g page lists Companion, but Sony's repair instructions also say support ends when the model's carrier repair period has ended. Current E2003 eligibility and offered CDA are therefore **UNKNOWN**, not a verified restore route. The latest official Windows installer was fetched and displayed its EULA under Wine, but it was not installed or connected to the device. No repair or device write was performed; details are in [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md).

## Probability checkpoint — 2026-10-14

To avoid conflating “can build an image” with “can safely run it on the handset,” estimates are separated by outcome. These are engineering judgments from current evidence, not statistical guarantees:

| Outcome | Current estimate | Evidence / gate |
|---|---:|---|
| Produce and inspect an offline stock-derived API 19 system-image POC from available E2003-family material | ~85% | Full R3A and R10A system images can be reconstructed and parsed; 99.65% and 99.74% of common captured `/system` file paths respectively match live R7A. Remaining work is image modification/repack QA; this is not a device boot estimate. File metadata/boot partitions are not compared and both candidate CDAs differ. |
| First boot of a minimal stock-derived build on this R7A handset | ~70–75% conditional; low-to-moderate confidence | 99.65% R10A and 99.74% R3A common `/system` file matches, plus independent R3A/R10A/TWRP boot-kernel evidence and historical E2003 recovery p9 mapping. Assumes reported unlock is true, live R7A boot bytes match this E2003 build-family payload, recovery target maps correctly, and R7A-specific files are preserved. None of those boot/recovery assumptions has been tested on-device. |
| Safely recover if first boot fails using evidence already in hand | <50% | Flashtool's E2003 profile is now verified, improving host-tool confidence, but the available FTF mismatches CDA and is untrusted; neither Flashtool restore nor the historical recovery image has been tested on R7A. |
| Build a newer AOSP/LineageOS ROM for E2003 | <20% | Exact kernel source/config and device tree are still absent; no reproducible port was found. |

The ≥70% threshold is met only as a **conditional estimate for first boot of a minimal stock-derived build**, not as an observed result or an overall safe-ROM success probability. The R3A comparison raises confidence in the shared userspace and confirms the full mirror copy's integrity against its published MD5; it does not raise the overall safe install-and-recovery estimate because the live boot bytes and rollback route remain unverified. First-boot estimate remains ~70–75% conditional with low-to-moderate confidence. Safe recovery after a failed boot remains below 50% on present evidence. No ROM has been built or booted on the phone. The highest-value next step is still an exact, traceable restore package and confirmation of Sony's service repair availability; then independently review recovery provenance and—only after separate authorization—test recovery/rollback before any ROM write. No device write or image boot has been performed.

### Root evidence update — 2026-10-14

A Turkish E4g forum discussion adds an exact-build but unverified KingRoot report: an owner says an APK with a newer exploit database rooted an E2003 after Sony repair installed `25.0.A.2.31`. In that same thread, the owner says the device had previously been rooted, and another participant questions whether residual root access survived the repair. A second E4g procedure describes KingoRoot after installing `25.0.A.1.28`; a 4PDA E2003 user reports KingRoot-to-SuperSU remained functional on `25.0.A.2.31` but does not identify the original root procedure. The source thread does not establish CDA `1293-7358 R7A`, clean-stock reproducibility, a trustworthy APK/hash, or safe behavior. This raises confidence that historical E4g root exploits existed, but it does **not** change the ROM first-boot or rollback estimates. No such software was acquired or executed. Details are in [ROOT_METHODS.md](ROOT_METHODS.md).

**Interpretation of the requested 70% bar:** the estimate for first boot is around 70–75% only under explicit assumptions. We cannot honestly rate the end-to-end goal—install a ROM and retain a reliable recovery path—at 70% while the restore route is under 50% and the recovery image has never been tested on R7A. The next evidence that can move that end-to-end estimate materially is a confirmed restore offer/package plus a separately authorized, successful recovery/backup/restore validation. Until then, “70% overall” is not met. The connected handset was rechecked read-only on 2026-10-14: exactly one authorized E2003 reports CDA `1293-7358 R7A`, Android 4.4.4/API 19, kernel 3.10.48+, and p9=`fotakernel`; ADB shell is uid 2000 and `/system/bin/su`/`/system/xbin/su` were not found. This does not establish bootloader lock state. No raw partition data was read.

**Root research note:** a 2016 community report describes KingRoot on E2003/Android 4.4.4/build `25.0.A.2.31`, but the handset had previously been rooted and commenters questioned whether residual files explain the result. Treat it as weak evidence only; APK/version/provenance, CDA and reproducibility are missing. It is not an approved procedure. See [ROOT_METHODS.md](ROOT_METHODS.md).
