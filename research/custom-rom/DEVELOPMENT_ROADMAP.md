# FarfarRemote OS development roadmap

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Immediate decision

Continue the currently working Android 4.4.4 stock launcher track. Treat FarfarRemote OS today as a dedicated Android configuration, not a ROM. **REPORTED by owner, 2026-10-14:** all current FarfarRemote features have now been tested and work on both App and OS editions. **VERIFIED** in a separate physical E2003 check: the active stream folder browser opened and restored the episode directory. Keep this working software as the control baseline.

## Prioritized gates

### Gate 1 — preserve baseline and collect exact sources

- Keep the current OS APK and source commit, app preferences and a private device audit.
- Confirm model/build/customization and reported bootloader state without rebooting or modifying.
- Find official Sony/traceable E2003 25.0.A.2.31 firmware and validate matching kernel source. The E2003 R10A UK package has been archive-checked and boot/FOTA/system payloads inspected offline. The system `/build.prop` identifies `1293-7276 R10A`, not the live R7A phone, and mirror provenance is not authenticated. It is analysis material only. The similarly named R7A Nextel-PE package is listed for E2006 and is excluded. A `callass` kernel-source mirror now compiles offline, but its generated config differs from observed live evidence and no Android product tree is present. Keep proprietary binaries out of public Git.
- **Exit:** exact firmware bundle and source/recovery provenance reviewed; restoration path documented.

### Gate 2 — offline stock image analysis (**partial progress**)

- **Done for the unverified R10A candidate only:** extracted `boot.sin`, `fotakernel.sin` and `system.sin` offline with bounds-checked readers; SIN integrity checks passed. Inspected the 3.10.48+ kernel ELF, cpio ramdisks, init scripts and fstab. Boot/FOTA share a kernel segment but have different ramdisks. Reconstructed `/system` is a 2,097,152,000-byte ext4 image; `/build.prop` confirms E2003 / 25.0.A.2.31 / API 19 / customization 1293-7276 R10A. Read-only e2fsck reports only an inode bitmap padding warning, so the filesystem is not recorded as a clean checker pass.
- New evidence: a complete captured R7A/R10A `/system` comparison shows 4,248/4,263 common paths byte-identical. A newly completed R3A candidate comparison shows 4,247/4,258 common paths byte-identical (99.74%); the full R3A FTF MD5 matches the AFH listing and its ZIP test passes. Both alternate CDAs remain non-restoration evidence. A retrieved historical E2003 TWRP candidate has the exact same kernel bytes as the R10A candidate and fstab maps p9 to recovery, matching the live `fotakernel` partition number. An offline repack tool assembles and validates a legacy boot-image container from Sony ELF payloads, but its boot metadata is not device-validated. A pinned `callass` kernel-source mirror now generates a configuration and compiles an ARM `zImage`; source provenance and final R7A config are still unverified. The generated config has an `IKCONFIG_PROC` mismatch against the observed handset. Still required: exact R7A inputs, valid stock boot parameters/DTB requirements and an authorized device boot/recovery test.
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
2. Validate the public kernel-source candidate: mirror provenance is unauthenticated and no exact R7A final `.config`/defconfig or source-to-live-kernel match is established. The candidate compiles with a legacy toolchain, but its current generated config differs from live observations.
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
| Produce and inspect an offline stock-derived API 19 system-image POC with FarfarRemote preinstalled | **Verified once** | The R10A ext4 image was modified offline; APK identity/API/signature were checked; APK readback matched byte-for-byte; SELinux label/owner/mode were inspected; and `e2fsck -fn` exited 0. This is not a device boot estimate. Base CDA differs and system metadata/boot chain are not R7A-matched. Details: [ROM_FEASIBILITY.md](ROM_FEASIBILITY.md). |
| First boot of a minimal stock-derived build on this R7A handset | ~70–75% conditional; low-to-moderate confidence | 99.65% R10A and 99.74% R3A common `/system` file matches, plus independent R3A/R10A/TWRP boot-kernel evidence and historical E2003 recovery p9 mapping. The new kernel mirror matches version/project clues but is not provenance- or config-verified. Estimate assumes reported unlock is true, live R7A boot bytes match this build-family payload, recovery target maps correctly, and R7A-specific files are preserved. These boot/recovery assumptions remain untested on-device. |
| Safely recover if first boot fails using evidence already in hand | <50% | Flashtool's E2003 profile and the kernel mirror improve tooling/source leads, but available FTF mismatches CDA and is untrusted; neither Flashtool restore nor historical recovery was tested on R7A. |
| Build the mirrored E2003/callass Linux kernel offline | **100% for this pinned source/toolchain combination (observed once)** | `makeMtk callass n k` produced ARM `zImage` and `vmlinux` with NDK r10e GCC 4.8. This is not a verified R7A kernel. |
| Build a newer AOSP/LineageOS ROM for E2003 | <20% | Kernel source candidate compiles, but its provenance/final config remain unresolved and no Android device tree or reproducible product build is available. |

The ≥70% threshold is met only as a **conditional estimate for first boot of a minimal stock-derived build**, not as an observed result or an overall safe-ROM success probability. The offline system-image POC demonstrates an editable ext4 base and compatible FarfarRemote APK, but no Sony SIN/FTF packaging, R7A boot chain, or on-device boot has been validated. Kernel-tree buildability is demonstrated offline, but source provenance, live R7A config, exact live boot bytes and a proven rollback/recovery route remain unavailable. First-boot estimate remains ~70–75% conditional with low-to-moderate confidence; safe recovery remains below 50% on present evidence. No ROM has been built as a complete firmware package or booted on the phone. The highest-value next step is a supported-host Xperia Companion preflight and exact, traceable restore path; then independently review recovery provenance and—only after separate authorization—test recovery/backup/restore before any ROM write. No device write or image boot has been performed.

### Root evidence update — 2026-10-14

A Turkish E4g forum discussion adds an exact-build but unverified KingRoot report: an owner says an APK with a newer exploit database rooted an E2003 after Sony repair installed `25.0.A.2.31`. In that same thread, the owner says the device had previously been rooted, and another participant questions whether residual root access survived the repair. A second E4g procedure describes KingoRoot after installing `25.0.A.1.28`; a 4PDA E2003 user reports KingRoot-to-SuperSU remained functional on `25.0.A.2.31` but does not identify the original root procedure. The source thread does not establish CDA `1293-7358 R7A`, clean-stock reproducibility, a trustworthy APK/hash, or safe behavior. This raises confidence that historical E4g root exploits existed, but it does **not** change the ROM first-boot or rollback estimates. No such software was acquired or executed. Details are in [ROOT_METHODS.md](ROOT_METHODS.md).

**Interpretation of the requested 70% bar:** the estimate for first boot is around 70–75% only under explicit assumptions. We cannot honestly rate the end-to-end goal—install a ROM and retain a reliable recovery path—at 70% while the restore route is under 50% and the recovery image has never been tested on R7A. The next evidence that can move that end-to-end estimate materially is a confirmed restore offer/package plus a separately authorized, successful recovery/backup/restore validation. Until then, “70% overall” is not met. The connected handset was rechecked read-only on 2026-10-14: exactly one authorized E2003 reports CDA `1293-7358 R7A`, Android 4.4.4/API 19, kernel 3.10.48+, and p9=`fotakernel`; ADB shell is uid 2000 and `/system/bin/su`/`/system/xbin/su` were not found. This does not establish bootloader lock state. No raw partition data was read.

**Root research note:** a 2016 community report describes KingRoot on E2003/Android 4.4.4/build `25.0.A.2.31`, but the handset had previously been rooted and commenters questioned whether residual files explain the result. Treat it as weak evidence only; APK/version/provenance, CDA and reproducibility are missing. It is not an approved procedure. See [ROOT_METHODS.md](ROOT_METHODS.md).

### Continued source and access investigation — 2026-10-14

- A fresh exact-CDA search still found no public `1293-7358 R7A` FTF. The currently visible [Sony Open Devices supported-device list](https://opendevices.sony.net/supported-devices-and-functionality) does not include E2003; its [open-source archive catalog](https://opendevices.sony.net/aosp-on-xperia-open-devices/downloads/open-source-archives) exposes newer archives, with no discoverable `25.0.A.2.31` E2003 source bundle. This is a catalog finding, not proof that no historical GPL tarball exists elsewhere.
- Direct on-device probe confirmed ordinary ADB shell cannot read even the first four bytes of live `boot` or `fotakernel` (`Permission denied`). The read data was discarded on the handset and no image was saved. Reproduce with `tools/probe_e2003_boot_read_access.sh`.
- The alleged 2018 E4g LineageOS 15 beta is not build evidence: the post itself says it was based on a Galaxy Note 8 custom ROM and provides no auditable sources, E2003 variant/CDA support, hashes or reproducible tests. It does not change the newer-ROM estimate.

The kernel-source mirror is a genuine additional lead, and the pinned tree has now produced an offline kernel build (see [BUILD_ENVIRONMENT.md](BUILD_ENVIRONMENT.md)); this does not authenticate the source, provide a final R7A config, or prove a device boot. These findings **do not raise the end-to-end safe-ROM probability above 70%**. The conditional first-boot estimate remains around 70–75% for a narrow stock-derived image under unverified assumptions; a recovery-backed ROM attempt remains below 70%. We should not relabel the former as the overall chance. The next evidence with enough leverage is an official/traceable restore offer or exact source package, then separately authorized recovery/backup/restore validation. Sony Companion's supported-host preflight remains outstanding; stop before any final repair action.
