# Recovery and restore strategy

## Linux Mint-only host route — 2026-10-15

The owner has confirmed Linux Mint is the only available host OS, so the
Windows/macOS Xperia Companion preflight is not currently actionable. Sony's
current Companion documentation lists Windows and macOS, not Linux
([Sony Companion requirements](https://www.sony.com/electronics/support/mobile-phones-tablets-tablets/articles/00236877)).
Do not treat Wine as an equivalent supported environment; prior Wine
enumeration did not verify repair availability or a retained firmware package.

There is a Linux-capable third-party path worth validating at the USB transport
level: [Sony Mobile Flasher / Flashtool](https://flashtool.net/download.html)
publishes a Linux release, and the pinned `Androxyde/devices` database has an
`E20XX` profile that recognizes E2003. These facts establish host/tool and
model-profile availability only. The profile includes broad Flashmode actions,
including boot, fotakernel and TA operations; it is **not** a safe restore
recipe. The currently available FTF candidate has CDA R10A/R3A mismatch, so it
must not be used as an R7A restore image.

**Safe Linux next step:** when the owner has the handset physically available,
enter Sony Flashmode using the model's documented hardware sequence and
observe only USB enumeration (`lsusb`/kernel log). Do not start Flashtool's
flash workflow, select partitions, or send a command. This would verify that
Linux sees the handset in Flashmode, not that it can restore the exact R7A
firmware. After transport verification, inspect Flashtool offline and establish
an exact, traceable R7A package plus a reviewed, narrowly scoped restore plan.
The handset must remain in normal Android if there is any ambiguity about the
button sequence or connection state.

The passive helper [`tools/observe_sony_usb_mode.sh`](tools/observe_sony_usb_mode.sh)
records only newly appearing Sony VID:PID values and exits. Run it before
connecting the powered-off handset in Flashmode, for example:
`research/custom-rom/tools/observe_sony_usb_mode.sh 120`. Sony's general
[Flashmode key guide](https://developer.sony.com/open-source/aosp-on-xperia-open-devices/get-started/flash-tool/useful-key-combinations)
says power off, hold Volume Down, then connect USB. That guide is for supported
Open Devices Xperia models and is not an E2003-specific service guarantee; the
observed USB ID must be recorded and interpreted as transport evidence only.
The helper was syntax-checked and smoke-tested with a one-second timeout while
the E2003 remained in Android. No mode transition was attempted.

No Flashtool binary has been downloaded or executed as part of this update.
Its published download page is a third-party origin and provides a SHA-1
checksum for the listed Linux release, which is useful for corruption checks
but is not a publisher signature or an independent authenticity proof.

## Fresh read-only ADB access check — 2026-10-15

The currently attached handset was re-identified without exposing its USB
serial in the report: `E2003`, Android 4.4.4/API 19, build `25.0.A.2.31`, CDA
`1293-7358 R7A`. ADB reports the shell as UID 2000 in SELinux domain
`u:r:shell:s0`; `ro.secure=1`, `ro.debuggable=0`, and `su` is not on PATH.
The `/data/local/bootanimation.zip` override is absent.

The read-only partition alias listing reconfirmed `boot -> mmcblk0p10`,
`fotakernel -> mmcblk0p9`, and `system -> mmcblk0p19`. ADB shell can stat the
boot block node (`root:system`, mode `0640`) but a one-block read to `/dev/null`
returns `Permission denied`; `fotakernel` is `root:root` mode `0600` and its
read is also denied. No raw partition data was obtained. No root command, reboot,
Fastboot transition, or write command was issued. Fastboot currently has no
connected device; this says nothing about what its bootloader would permit.

**Readiness effect:** this closes the safe ADB route to an exact R7A boot/FOTA
dump. An exact R7A firmware package with traceable origin, or a separately
reviewed read-only bootloader/BootROM extraction method, is still needed before
root-image work can be made firmware-exact. The R10A offline animation POC does
not substitute for that input.

### Owner-operated recovery-menu exit — 2026-10-15

The owner reported the handset was showing the Sony System Recovery menu with
`Continue Power Up`, `Safe Mode`, `Factory Reset`, and `Power Down`. They chose
`Continue Power Up`. Before that selection, Linux saw Sony USB `0fce:0c01` and
ADB reported the device as offline; Fastboot saw no device. Afterward, read-only
checks showed ADB `device`, Sony USB `0fce:51cb`, and properties matching
E2003 / Android 4.4.4 / `25.0.A.2.31` / CDA `1293-7358 R7A`. This demonstrates
a successful return from that menu to Android without a factory reset. It
does not test Flashmode, Fastboot writes, recovery image behavior, or restore
capability. No device command was sent while it was in recovery.

### Passive Linux Flashmode enumeration — 2026-10-15

After the owner attempted the non-writing USB check, the host observed a
disconnect followed by Sony USB `0fce:adde`, product string `S1 Service`, with
no ADB or Fastboot device. This is the expected Sony S1 service/Flashmode USB
transport. The prior normal-mode connection on the same USB port had been
read-only identified as E2003 / `25.0.A.2.31` / `1293-7358 R7A`, so this is
strong evidence that the handset reached S1 service mode. No Flashtool session,
loader transfer, Fastboot command, or partition operation was started.

**Readiness effect:** Linux Mint can enumerate the handset in service mode.
This confirms transport only; it does not establish a usable exact-R7A restore
package, safe partition selection, or successful repair. The phone must not be
treated as recoverable until those independent gates are closed.

Sony's [current E4g support page](https://www.sony.com.au/electronics/support/mobile-phones-tablets-mobile-phones/xperia-e4g)
still lists Xperia Companion (release date 2022-05-15), and the Sony E2003
family user guide documents Companion's Software repair function. This proves
the vendor utility was associated with this model family; it does **not** prove
that the current utility still offers firmware for CDA `1293-7358 R7A`, that
the unlocked handset is accepted, or that a resulting download can be retained
as an exact restore package. The repair workflow remains a lead to check on a
supported Windows/macOS host, stopping before any final repair confirmation.

## Fresh read-only prerequisite refresh — 2026-10-14

The repository's `tools/collect_e2003_prerequisites.sh` was run against the single authorized ADB device. It confirmed model/device `E2003`, board `callass`, Android 4.4.4/API 19, build `25.0.A.2.31`, CDA `1293-7358 R7A`, MT6752 platform string, and Linux `3.10.48+`. The live partition aliases report `boot -> mmcblk0p10`, `fotakernel -> mmcblk0p9` (32 MiB), and `system -> mmcblk0p19`; only partition metadata was read. `/proc/config.gz` is absent and ordinary ADB cannot read the boot command line. This refresh did not inspect raw partition contents or verify the owner-reported unlocked state. Temporary output was kept outside Git.

The pinned Flashtool E20XX FSC profile was also re-read locally at `Androxyde/devices` commit `4f354572579e62337d56a6b9319f7f8b31b3378a`. Its static sequence includes loader/partition-table, `preloader_s1sbl`, `secro`, `cache`, `boot`, `fotakernel`, `lk`, `logo`, `tee1`, `tee2`, `userdata`, `system`, `elabel`, and TA `writeTA:2127` / `writeTA:2212` operations. This is a broad service-flash recipe, not a narrow recovery procedure. It reinforces that a generic Flashtool profile cannot be treated as a safe rollback path; do not run it as a “restore test.”

**Readiness effect:** no new recovery or exact-R7A firmware was discovered, so the end-to-end safe-ROM estimate does not increase. A recovery path still requires either a supported-host Sony Companion preflight that identifies the exact handset and offered repair customization, or a traceable E2003/R7A-compatible stock package plus an independently reviewed restore procedure. Neither has been established.

## Current recovery position

### Fastboot temporary-boot capability audit — 2026-10-15

- **VERIFIED public documentation:** Sony's current Open Devices guide describes entering Fastboot and gives the `fastboot oem unlock` procedure. It does not document `fastboot boot`, E2003 image booting, or a recovery partition mapping for this S1 bootloader. This documentation gap is not proof that the command is unsupported.
- **VERIFIED historical E2003-specific report:** the XDA recovery post cited below tells users to `fastboot flash recovery recovery.img`; the available post does not describe a temporary `fastboot boot` test. Therefore it supports a historical *write* path claim, not a non-persistent test-boot claim.
- **Search result:** targeted searches for `E2003 fastboot boot`, the exact `S1_Boot_MT6732_TC9PRA_9` identifier, and Sony S1 temporary boot did not surface an exact-device report establishing support. Other Sony/Xperia models and generic Android Fastboot instructions are not transferable proof.
- **Conclusion:** temporary boot remains **UNKNOWN**. It must not be assumed safe or available. Even if supported, `fastboot boot IMAGE` transfers and executes an image; it is not a read-only probe. Any later live capability test needs a separately reviewed, exact image and explicit authorization for that image-transfer action. Do not test with the unaudited historical TWRP artifact.
- **Best next non-destructive evidence:** obtain the exact bootloader protocol/command implementation for this S1 release from an authenticated Sony source, or locate a reproducible E2003 report that records the exact bootloader version, command response, image identity and successful return to Android. A live `fastboot boot` attempt is not needed to continue offline ROM preparation and should remain outside this research-only phase.

- Sony documentation consulted: [How to unlock the bootloader](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader).

- **VERIFIED:** Sony firmware exposes a `fotakernel` partition alias; there is no separately named `recovery` partition in the live read-only partition map.
- **REPORTED, untrusted lead:** a 2017 E4g blog post links unsigned/signed TWRP ZIP files and describes installing them through the stock recovery's update path. It does not establish exact support for E2003 vs E2006/E2053, firmware 25.0.A.2.31, or CDA 1293-7358 R7A; the linked payloads have not been acquired, hashed, source-audited or tested. The described stock-recovery sideload path is not a safe read-only probe. Do not run it.
- **VERIFIED historical E2003-specific recovery artifact; NOT device-verified here:** the archived original post in the [XDA E4g TWRP thread](https://web.archive.org/web/20161114114427id_/http://forum.xda-developers.com/general/rooting-roms/twrp-recovey-sony-xperia-e4g-t3425174) explicitly says the author built TWRP for `e4g(e2003)`, reports all functions tested, and instructs `fastboot flash recovery recovery.img` after bootloader unlock. The linked `TWRP_2.8.7.0_for_E4g` image was retrieved from [MediaFire file ID 52kgi3g3c6ec4ul](https://www.mediafire.com/file/52kgi3g3c6ec4ul/recovery.img/file) for offline analysis only. Its observed SHA-256 is `39c036cf31523d986f6ffe052aa54b1787ecd0b1b864434bfcf910c915e162e1`. It is a legacy Android boot-image-format container; embedded properties identify E2003, Android 4.4.4/build `25.0.A.2.31`, API 19, board `callass`, platform MT6752, but customization R5A rather than the live R7A. The kernel payload hash exactly matches the kernel segment in the unverified R10A `boot.sin` candidate (`4115fd4775103d21c622abf22b27e260100d005aa5f5b22ed1fd9dfc183e0d36`). Its recovery fstab maps `/recovery` to `mmcblk0p9`; the live read-only map calls p9 `fotakernel`. These are strong exact-model/build-family clues, but the image has no reproducible source/build provenance or trusted publisher checksum and has not been booted on this handset. Do not flash or temporary-boot it.
- **ADDITIONAL cross-source match, not another recovery:** partial offline inspection of the AFH E2003 R3A / `25.0.A.2.31` package shows its `boot.sin` kernel and ROOTFS segment hashes match the R10A E2003 package exactly; the common kernel also matches historical TWRP. AFH lists MD5 `d47d25c4bdadb3116d2f39c94a69a4bc`, but the full package was not downloaded and that archive hash is unverified. This adds confidence in a shared E2003 build-family boot payload, not in the R7A recovery target, recovery function, or restore route. Details: [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).
- **VERIFIED community status report:** an /e/OS device request says there is no official or unofficial LineageOS build for the E4g as of April 2022. This is not proof no abandoned/private port ever existed, but it supports the present finding that there is no maintained public ROM baseline located for this model.
- **UNKNOWN:** whether this bootloader supports `fastboot boot`, whether `fastboot flash recovery` aliases p9 on this device/firmware, and whether the historical TWRP mounts the live R7A data/system correctly. A read-only `getvar partition-size:recovery` returned empty while `partition-size:fotakernel` returned `0x2000000` (32 MiB). Fastboot getvar results do not necessarily prove which target names its flash command accepts. The community author's positive report is not an independent test. See the 2026-10-15 Fastboot capability audit above.
- **VERIFIED transport/product, unlock still REPORTED:** a temporary Fastboot session identified `product: E2003` and bootloader `1290-9780 S1_Boot_MT6732_TC9PRA_9`; `secure: yes`; `getvar unlocked` was blank and `oem device-info` returned unknown command. The handset was returned to Android and ADB re-confirmed E2003 / 25.0.A.2.31 / 1293-7358 R7A. No image or write command was sent. These queries do not independently establish that the bootloader is unlocked.
- **VERIFIED official software-repair route exists; exact-device outcome unknown:** the [Sony Xperia E4g Android 4.4.4 user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf) documents PC Companion/Software repair for the E2003 family, and Sony's current [repair instructions](https://www.sony.com/electronics/support/mobile-phones-tablets-tablets/articles/SX604601) still describe reinstalling device software through Xperia Companion. Sony says repair overwrites internal storage. **UNKNOWN:** whether today's Companion still downloads firmware for this discontinued model, recognizes this E2003 while its bootloader is reportedly unlocked, and offers a repair package usable as ROM rollback. So Companion is a promising vendor recovery candidate, not a verified recovery base. Its supported desktop hosts are Windows/macOS, not Linux Mint; the Linux Wine enumeration result does not substitute for testing on a supported host.

### Candidate image analysis update — 2026-10-14

An unverified mirror supplied an FTF whose internal manifest identifies `E2003`, build `25.0.A.2.31_R10A`, and `CustomizedUK`, but leaves both `cda` and `revision` blank. Its locally observed SHA-256 is `ffb5b42cc196eea4d6651817992bf230a3efdbef1e50ac68eb93866aeec8f37b`; the mirror provides no trusted comparison hash. ZIP CRC/integrity testing passed. This is **not** a match to the phone's `1293-7358 R7A` and is not an approved restore base.

The `boot.sin` and `fotakernel.sin` payloads were decoded offline and checked against their embedded SHA-256 values. Both are Sony-format ARM ELF images, not Android `boot.img` files. The boot ELF contains a 3.10.48+ kernel and an Android init cpio ramdisk; the FOTA ELF has a distinct FOTA ramdisk. This establishes an image-analysis lead only. It does not validate a recovery image, a bootloader path, or a safe image conversion. No `boot.img` conversion, patch, repack, or device write was attempted.

## Recovery route required before root or ROM

1. **Promising official route to validate:** on a supported Windows/macOS host, inspect the current Xperia Companion repair flow for E2003 while stopping before the final confirmation that starts repair. Record whether it recognizes E2003 and any offered software/customization metadata. Do not start repair during this preflight. A later actual repair test would erase device data and needs separate explicit authorization.
2. Find an independently traceable exact E2003 stock package matching CDA `1293-7358 R7A`; the R10A Customized UK mirror candidate is insufficient. Verify provenance/checksums and inspect included images offline.
3. Preserve original image copies and hashes offline, with two independent copies. The app's preferences can be backed up logically only through normal app UI/export; do not assume an image restore retains user data.
4. Establish what Sony Companion would restore and whether it is adequate as a recovery route, or establish an exact FTF restore method using documented Sony/Flashtool tooling. No actual repair/flash trial here.
5. Fastboot product/version were checked read-only after a temporary, reversible transition and Android was restored. Further read-only queries are acceptable; do not issue unlock, erase, flash, format, boot, or other image-transfer commands without separate authorization and a reviewed artifact.
6. Obtain a recovery image explicitly built for E2003 single-SIM and matching layout; inspect source, build recipe and checksums. Test first only if a safe temporary boot path is proven.
7. Before any separately authorized write, prepare a recovery checklist, charger/cable, host tools, exact image hash, rollback path and expected data-loss statement.

### Public recovery leads reviewed — 2026-10-14

- Sony's [Xperia E4g support page](https://www.sony.com.au/electronics/support/mobile-phones-tablets-mobile-phones/xperia-e4g) lists a Companion entry and the E4g user guide documents repair; Sony's [general Companion matrix](https://www.sony.jp/xperia/support/software/xperia-companion/) marks Software Repair available for all Xperia products. However, Sony's [repair instructions](https://support.sony.jp/electronics/support/articles/00280550) explicitly caveat that support ends when a model's carrier repair period ends. Therefore present E2003 eligibility and the firmware/CDA offered by repair remain **UNKNOWN**, not a verified restore path. Repair deletes user data; no repair was started. Sony's current [Companion page](https://www.sony.com/electronics/support/mobile-phones-tablets-tablets/articles/00236877) says the official desktop app is for Windows 10 (64-bit, ESU) / Windows 11 or supported macOS; pre-`24.9.1.202408201019` Windows builds are no longer supported.

#### Current Sony Companion installer check — 2026-10-14

The latest installer was downloaded from Sony's official `app.swup.update.sony.net` endpoint to `/tmp` for a non-device test. The installer identifies itself as `26.7.1.202608190756`; its SHA-256 is `17dabeaae83f7b68e8a20a9678619637bce5b1efb0645d09b894e986bb082dda`. Running it under Wine 9.0 on Linux displayed Sony's license agreement. The agreement was not accepted, no installation was completed, and the attached phone was not contacted by Companion. This confirms the current official installer is reachable, but does not establish E2003 detection, repair eligibility, offered customization, or a restore route. The downloaded installer is not in Git. A model-specific preflight still requires using Companion on a supported Windows/macOS host and stopping before the final repair confirmation.

- The [Flashtool public E20XX device profile](https://github.com/Androxyde/devices/tree/master/E20XX) explicitly recognizes E2003 and contains a Sony Flashmode FSC recipe. Read-only source inspection confirms the generic profile supports stock firmware flashing but has no bundled `bootkit` helper for custom recovery; the FSC sequence also includes boot/FOTA/system and security-related operations. This establishes a plausible host utility for an exact, authenticated stock FTF, not an available matching package or verified recovery/rollback. No Flashtool action was performed on the phone.

- [Dian Ariyanto's 2017 E4g TWRP post](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/) links two ZIPs through third-party redirect/file hosts and describes temporary/permanent recovery installation. It provides no source repository, build identity, cryptographic digest or variant/CDA matrix. The page's broad “E4g” label is insufficient for the single-SIM E2003. Treat the files and procedure as **unverified and not approved**; do not test its stock-recovery sideload procedure on the phone.
- The archived [XDA TWRP thread](https://web.archive.org/web/20161114114427id_/http://forum.xda-developers.com/general/rooting-roms/twrp-recovey-sony-xperia-e4g-t3425174) contains the author's explicit E2003 build and successful-function claim. We retrieved and statically inspected the linked image; its SHA-256 and device/build properties are recorded above. The author describes flashing it to the recovery target, but there is no independent test log, signed checksum, source/build recipe, or proof for live R7A. Treat as a credible candidate, never as an already validated recovery.
- A 2019 [E4g recovery troubleshooting thread](https://www.elektroda.pl/rtvforum/topic3592260.html) reports a CWM flash attempt failing with `partition recovery not found`; after advice to unlock the bootloader and use TWRP, the poster later says TWRP was installed. The exact handset variant, command and TWRP build are not given, so this is corroboration that E4g recovery installs were possible, not evidence that `recovery` is the valid Fastboot target on our E2003. It is consistent with our blank `partition-size:recovery` query and reinforces that target alias behavior must not be guessed.
- The [E4g /e/OS device request](https://community.e.foundation/t/sony-xperia-e4g-e2003/40466) reports no official or unofficial LineageOS build in 2022. A separate [2018 blog post claiming an E4g LineageOS 15.0 Oreo beta](https://dianariyanto.com/install-custom-rom-sony-xperia-e4g-lineage-os-15-oreo/) exists. It says the port is based on a Samsung Galaxy Note 8 Oreo custom ROM and links ROM/GApps through third-party file hosts; it gives no source repository, exact E2003/E2006/E2053 compatibility, hash, build log or independently reproduced result. This establishes a **reported ROM claim**, not a verified E2003 ROM. We did not download or run it.
- A contemporaneous [2016 E4g community-thread search result](https://forum.android.com.pl/topic/234990-xperia-e4g-e2003-e2006-e2053-w%C4%85tek-zbiorowy/285) says an E4g recovery had appeared and cautions that ROM development was stalled by trouble unpacking `boot.img`. This is secondary, unverified discussion rather than a build record. Our present offline ELF extraction and container POC solve only the mechanics of parsing/repacking the available candidate payloads; they do not establish the missing R7A header/boot parameters, device tree, recovery safety or a bootable ROM. Do not count that old post as an existing ROM source.

### Current device-side read-only status — 2026-10-14

ADB currently sees one authorized E2003 with build `25.0.A.2.31`, customization `1293-7358 R7A`. A temporary read-only Fastboot probe reconfirmed product E2003 and bootloader `1290-9780 S1_Boot_MT6732_TC9PRA_9`; `secure: yes`; `getvar unlocked` and `partition-size:recovery` were empty. Fastboot reported both `partition-size:boot` and `partition-size:fotakernel` as `0x2000000` (32 MiB). The phone was returned to Android and ADB reconfirmed the original build fingerprint. The live map identifies `boot` as `mmcblk0p10` and `fotakernel` as `mmcblk0p9`; no raw partition data was read. These queries do not independently confirm unlock state, Fastboot flash alias behavior, or temporary boot support. No image or write command was sent.

The complete accessible R7A/R10A tree comparison (4,248/4,263 common paths identical) improves confidence in userspace relevance. The retrieved historical E2003 TWRP image adds boot-stack and p9 mapping evidence, but does not validate recovery or restore on R7A. The exact restore/recovery gate remains **BLOCKED**.

An additional retrieval attempt used the two download links and the page's “mirror” link. The page identifies filenames `unsigned_twrp_sony-xperia-e4g_temp.zip` and `signed_twrp_sony-xperia-e4g.zip`, but all three redirects returned HTTP 403 through the available fetch route. Exact bytes, hashes, signing identity, install scripts, target partition and supported E2003 firmware therefore remain unavailable for audit. The article's own procedure installs a temporary package through stock recovery and then permanently installs recovery; that is a modifying procedure, not a read-only check, and is not suitable to test without a separately established restore path and explicit approval.

## Protected areas and constraints

Do not write `ta`, `nvram`, `proinfo`, `protect1`, `protect2`, `seccfg`, `secro`, `tee1` or `tee2`. Never use a generic MTK scatter/preloader package. Never flash E2033/E2043 dual-SIM or other Xperia/MT6732/MT6752 images.

No firmware or recovery image is in this repository. The R10A candidate and historical TWRP image exist only under `/tmp`; both are unverified for restoration to this R7A device. Recovery readiness remains **BLOCKED** until a restorable exact/official base and a separately authorized, reviewed recovery test are available. No root/custom ROM write is acceptable.


### Offline analysis of the retrieved historical recovery — 2026-10-14

The image was identified as an Android boot image with a 2,048-byte page. Its legacy header reports kernel size 6,325,338 bytes, ramdisk size 6,068,355 bytes, kernel address `0x40008000`, ramdisk address `0x44000000`, tags address `0x4e000000`, and command line `bootopt=64S3,32S1,32S1`. The kernel payload SHA-256 is exactly the same as the R10A candidate's stock boot kernel segment. The ramdisk's `/etc/recovery.fstab` identifies p9 as recovery; read-only live partition mapping identifies that same p9 as `fotakernel`. This strongly supports a shared E2003 boot stack and partition layout.

### Recovery fstab cross-check against the live R7A map — 2026-10-14

A read-only ADB listing of `/dev/block/platform/mtk-msdc.0/by-name` confirms that the historical image's `/system`, `/cache`, `/data`, `/boot`, `/logo`, `/nvram`, `/lk`, `/proinfo`, and `/protect*` fstab paths resolve to the same live partition aliases. The fstab's raw recovery path `/dev/block/platform/mtk-msdc.0/mmcblk0p9` is exposed as a symlink to `/dev/block/mmcblk0p9`, and the live map labels p9 `fotakernel`. Current `/proc/mounts` confirms system, userdata and cache are ext4, matching the recovery fstab's filesystem declarations. This is a stronger static partition/filesystem match than the prior alias-only comparison; it does not establish that TWRP can boot, mount reliably, or restore data on R7A.

The same fstab marks `nvram`, `proinfo`, `protect1` and `protect2` as backup-enabled, and marks several boot/security-related entries as image-flashable. These areas are sensitive. If this candidate is ever evaluated under a separately authorized recovery test, do not run a broad “select all” backup or any restore/flash operation; first review each selected target and keep NVRAM/TA/security partitions out of any write path.

The full recovery file is 12,398,592 bytes, smaller than the live 32 MiB `fotakernel` partition, but size fit alone does not establish a valid flash target or safe image. The first XDA post's supported-device statement is specific to E2003; its recovery properties report CDA/customization `1293-7242 R5A`, so this does not establish R7A validation. Binary identity and static parsing are verified locally; successful recovery boot, touch/storage mounting, backup/restore, and actual rollback remain **UNKNOWN**. The image must not be treated as safe merely because its header parses.

The checks are reproducible with `tools/verify_e2003_recovery.py`, which reads only a local recovery image and an offline stock kernel segment. On the retrieved artifact it reports `static_checks=PASS`: E2003 / API 19 / build `25.0.A.2.31`, boot header `N_S218`, the expected MediaTek command line, exact stock-kernel SHA-256 match, `/recovery` fstab mapped to p9, and an image size below the observed 32 MiB partition capacity. The script's scope explicitly excludes boot, flash, mount, and restore behavior. Example:

```sh
python3 research/custom-rom/tools/verify_e2003_recovery.py \
  /path/to/recovery.img /path/to/e2003-stock-kernel-segment.bin
```

The verifier was also checked against a deliberately mismatched kernel (exit 1 / `static_checks=FAIL`) and a non-Android input (exit 2 / header error), so a parsed but mismatched image is not reported as passing.

### Ordinary ADB read-access probe — 2026-10-14

The connected handset was checked again without rebooting. It identifies as E2003 / `25.0.A.2.31`; `adb shell id` reports UID 2000 (`shell`). A bounded probe attempted to read four bytes each from the `boot` (p10) and `fotakernel` (p9) block devices and immediately discard those bytes to `/dev/null`. Both returned `Permission denied`; no block image was created. The reproducible helper is [`tools/probe_e2003_boot_read_access.sh`](tools/probe_e2003_boot_read_access.sh). This removes ordinary ADB as a way to obtain exact live boot/FOTA backups under the current access level. It neither establishes that root is impossible nor tests Fastboot read/write behavior. **Recovery/rollback remains unverified.**

### Fresh ROM-source catalog review — 2026-10-14

**Update:** a public [E2003 kernel-source mirror](https://gitlab.com/sobotkama/android_kernel_sony_e2003), pinned at `2a84825e8268393267e454e35a00f80d48c58949`, contains Linux 3.10.48 and `callass`/MT6752 source configuration. Its Sony provenance is not independently authenticated; the final R7A config is unknown, the bundled recovery fstab uses stale MTD/YAFFS2, and the candidate kernel has only been compiled offline. It is a kernel source lead, not a recovery image or complete ROM tree. See [BUILD_ENVIRONMENT.md](BUILD_ENVIRONMENT.md).

The [Sony Open Devices supported-device page](https://opendevices.sony.net/supported-devices-and-functionality) describes support for selected models and its current list does not include E2003. The [Sony open-source archive catalog](https://opendevices.sony.net/aosp-on-xperia-open-devices/downloads/open-source-archives) currently displays recent firmware archives, with no discoverable E2003 `25.0.A.2.31` source bundle. This does not rule out a historical GPL archive elsewhere. The separate public kernel mirror noted above supplies a kernel source candidate, but no device tree, verified final R7A defconfig, reproducible build, or complete ROM input set. The separately reviewed Android 8 beta claim is not reproducible and supplies none of these missing inputs.

### MediaTek BootROM readback candidate — research only, 2026-10-14

The upstream [bkerler/mtkclient](https://github.com/bkerler/mtkclient) repository, pinned at `7cb40e727727dfe3faa065eefb29b16ed29bbdf1` on 2026-10-14, contains an explicit `0x6752` chip configuration and names an MT6752 payload. Its usage guide documents read commands `mtk.py r boot boot.bin` and `mtk.py r <partition> <output>`. This aligns with the live E2003's reported `MT6752` platform and makes the tool a plausible lead for read-only dumps of the exact live `boot` and `fotakernel` partitions if BootROM entry, security state, USB handshake and Download Agent initialization all cooperate. The current device database does not identify Xperia E2003; generic SoC support is not proof of Sony S1/MediaTek secure-boot compatibility. No MTKClient source or binary was run against this phone, no BROM mode was entered, and no bytes were read. This is **UNKNOWN / unverified**, not an established root method or restore route. See the pinned [MT6752 configuration](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/config/brom_config.py) and [read-flash usage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/README-USAGE.md#read-flash).

Any future physical investigation needs a separately authorized session, pinned source/version and an audited read-only operation plan limited to partition-map metadata plus `boot`/`fotakernel` reads. Do not use write, erase, format, unlock, `reset`, NVRAM/TA or security-area commands; keep device-specific images private and hash them. The read command may still execute a temporary BootROM/DA payload in RAM and power-cycle the handset, so this has not been treated as ordinary ADB inspection. Exact live boot dumps would improve image fidelity, but would not prove a rollback path unless a matching Sony flashing route is also validated.

### Bounded MTKClient boot/FOTA read helper — prepared, not yet run on device

MTKClient commit `7cb40e727727dfe3faa065eefb29b16ed29bbdf1` was cloned and inspected offline. Its code includes MT6752 configuration and Sony BootROM VID/PID entries (`0fce:f200`, plus other Sony families); the live Android connection enumerates as `0fce:51cb`, which is not on that allowlist. The `r` CLI path routes to `readflash`; separate commands handle writes/erase. This is source-level review, not a guarantee against tool defects or Sony-specific behavior.

**Chip-ID caveat:** Sony's public specification calls the E2003 SoC MT6732, while the live OS/kernel identify their platform as MT6752 and the bootloader string contains `MT6732`. This mapping is unresolved. The pinned MTKClient tree has an explicit `0x6752` configuration but no `0x6732` entry. The helper does not force a hardware-code override; if the BootROM reports an unsupported code or an unexpected DA/security state, stop and preserve the log rather than trying another chipset profile.

**Physical-entry caveat:** No verified E2003-specific instruction for entering MTK BootROM has been found. Sony documents Volume Down + USB as Flashmode and Volume Up + USB as Fastboot; generic MTKClient instructions do not establish that those combinations override this Sony S1 boot chain. A monitored Volume Up + Power/USB attempt on this exact handset produced Sony Fastboot (`0fce:0dde`), not the wrapper's expected `0fce:f200` BROM ID; details are recorded below. Do not repeat generic key attempts or pass Sony Fastboot/Flashmode IDs to MTKClient. The next physical lead requires an authenticated E2003 board/service document or a documented Sony service route. Sources: [Sony key combinations](https://developer.sony.com/open-source/aosp-on-xperia-open-devices/get-started/flash-tool/useful-key-combinations), [pinned MTKClient usage guide](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/README-USAGE.md).

#### Physical USB mode observation — 2026-10-14

A monitored, reversible attempt was made with the E2003 powered off and connected while holding Volume Up + Power. USB changed from normal Sony Android (`0fce:51cb`) to Sony `0fce:0dde`, then disappeared when disconnected. The `0fce:0dde` ID is identified in Sony-device USB reports as **S1Boot Fastboot**; this is consistent with Sony's documented Volume Up + USB Fastboot key, not MediaTek BootROM. No `0fce:f200` BootROM interface appeared, MTKClient was not run, and no command was sent to the phone in that mode. After normal reconnection, ADB again reported E2003 / `25.0.A.2.31` / CDA `1293-7358 R7A`. No data or partition was read or changed.

This result resolves the previous generic button-combination question: repeating Volume Up + Power/USB is not a useful BROM probe on this handset. Do not try other random key combinations. An exact BROM entry route remains **UNKNOWN**; the next credible physical lead is an authenticated E2003 board/service document identifying test pads and board revision, or a documented Sony service mode. The surfaced E4g service-manual index is paywalled and does not expose a board-specific testpoint diagram, so it is not sufficient to guide opening or shorting the handset. The checked-in MTKClient read wrapper remains gated on an exact `0fce:f200` match and must not be relaxed to accept `0fce:0dde`. References: [Sony's key-combination guide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/flash-tool/useful-key-combinations), [USB ID observed as Sony S1Boot Fastboot](https://www.claudiokuenzler.com/blog/746/how-to-install-custom-android-rom-sony-xperia-z2-d6503), [E4g service-manual index](https://vinafix.com/threads/sony-xperia-e4g-e4g-dual-2003-e2006-e2033-e2043-e2053-service-manual.33711/).

[`tools/read_e2003_boot_partitions_mtkclient.sh`](tools/read_e2003_boot_partitions_mtkclient.sh) is a tightly bounded wrapper. It pins that exact source commit, requires no authorized ADB device online, requires exactly one `0fce:f200` Sony BootROM USB device (generic MTK IDs and other Sony product IDs are rejected), and hardcodes reads of only `boot` and `fotakernel`. It refuses outputs inside the repository, requires each captured file to be 32 MiB, and hashes the pair. It has no command/argument passthrough for MTKClient write, erase, format, unlock, or reset commands. A smoke check confirmed that it aborts with the ordinary Android ADB session still connected (exit 3) before opening an MTKClient session. Syntax validation passed. **It has not been run in BootROM mode.** The read path may upload a temporary loader/payload to RAM, invoke an SoC security-bypass routine, and reset/power-cycle the device. Soft-brick recovery would still depend on a separate Sony repair route; no guarantee is made. This readback could obtain exact live boot/FOTA inputs, but it is not itself a restore path.

The reviewed source and isolated Python environment are local, outside Git. Once the phone is physically in BootROM mode, a candidate invocation is:

```sh
mkdir -p /path/private/e2003-mtk-read
research/custom-rom/tools/read_e2003_boot_partitions_mtkclient.sh \
  /path/to/pinned/mtkclient /path/to/venv/bin/python \
  /path/private/e2003-mtk-read
```

Use a private location with at least 64 MiB free. Do not upload or commit the resulting firmware binaries. A clean readback is only the next evidence gate; boot/recovery still requires a separately reviewed and authorized write/restore experiment.

### Follow-up source and permission check — 2026-10-14

A targeted public search for the historical recovery filename, its `N_S218` header, and its XDA author (`n_s218`) found no source repository, device tree, signed checksum, or reproducible build recipe. The image remains a binary-only, unaudited recovery lead. Newly indexed firmware results still identify other customizations (including E2003 R10A and E2006 R7A); none matches this handset's E2003 / CDA `1293-7358 R7A`. A filename mentioning `R7A` is not sufficient to treat the E2006 package as compatible.

The connected device was checked without rebooting Android. `adb shell` reports UID 2000 (`shell`); `/dev/block/mmcblk0p10` (`boot`) is `root:system` mode `0640`, while `/dev/block/mmcblk0p9` (`fotakernel`) is `root:root` mode `0600`. The shell is not in group `system`; the system exposes no `su` binary at `/system/bin/su` or `/system/xbin/su`. Android boot-lock properties were empty. These metadata checks explain why ordinary ADB cannot produce exact boot/FOTA backups; they do not prove root impossible or independently determine bootloader unlock status. No partition bytes were read.

After the preceding update, the phone was deliberately rebooted into Fastboot solely for read-only `getvar` checks, then returned with `fastboot reboot`. Fastboot enumerated product `E2003`, `secure: yes`, `partition-size:boot=0x2000000`, and `partition-size:fotakernel=0x2000000`; `getvar unlocked` and `partition-size:recovery` were empty. Android came back with the same `Sony/E2003/E2003:4.4.4/25.0.A.2.31/4Pf_Nw:user/release-keys` fingerprint. No image was transferred and no write/erase/unlock command was issued. The empty unlock field still leaves the owner's unlocked report **unconfirmed**.

**Readiness effect:** no recovery path was verified. Keep the first-boot estimate conditional and the safe end-to-end estimate below 50%; do not count the R10A/E2006 firmware leads, the binary-only recovery, or empty lock properties as rollback evidence. The next material gate still requires a supported-host Xperia Companion preflight that shows a repair offer for this exact handset, or another exact and traceable recovery/restore base.

### Additional firmware trust-chain/source search — 2026-10-14

The E2003 R10A and R3A FTFs contain byte-identical `loader.sin` entries (279,788 bytes; SHA-256 `3f9c2a29f35bbbc18139f34a09fae7238323ceb52ac2e098a06d5278c573b729`) labelled `S1_Root_bee6`. Offline RSA/SHA-256 checks confirmed that the root certificate's self-signature and the `S1_SW` certificate signature verify against this embedded root. This corroborates a shared loader and an internally consistent certificate chain across these two community-hosted E2003 25.0.A.2.31 packages. It does not authenticate either download: Sony documents a hardware-rooted chain where Boot ROM holds the Sony Root CA public key, and we have not matched the embedded root fingerprint to that immutable device trust anchor or verified the SIN signature over payload data. More importantly, neither package matches the handset's E2003 `1293-7358 R7A` customization. Search results advertising R7A for E2006 or E2003 CDA `1293-9486` are not compatible restore evidence. Details and sources are in [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).

**Readiness effect: unchanged.** We gained an internally verified certificate relationship and stronger E2003/build-family component match, but no exact restore package, trusted authenticity proof, readable live boot image, or tested rollback. The safe end-to-end ROM path therefore remains **below 50%** on current evidence. Raising the estimate to 70% without one of those material gates would misstate risk. Highest-value next steps are an exact Sony Companion repair preflight on a supported host, discovery of a traceable E2003 R7A/compatible stock package, or a separately authorized read-only attempt to acquire exact live boot/FOTA images followed by identification of a tested recovery path.

### Fastboot partition fetch probe — 2026-10-14

With the exact E2003 attached, host Fastboot 34.0.4's documented `fetch` operation was attempted against `boot` after read-only checks of product and partition sizes. The bootloader returned `Unable to get max-fetch-size. Device does not support fetch command.` No partition data was returned. Fastboot briefly created a zero-byte host output file before the error; it was deleted. The handset was returned with `fastboot reboot`, and ADB then reconfirmed the original E2003 / `25.0.A.2.31` / `1293-7358 R7A` fingerprint and UID 2000 shell. No flash, erase, unlock, format, or partition write command was issued. This closes the standard Fastboot `fetch` path on the installed bootloader; it does not rule out Sony service software or a separately reviewed MTKClient read path. The latter may run temporary Download Agent code and is not authorized by this probe.

**Readiness effect:** unchanged; direct boot/FOTA backup remains unavailable through ordinary ADB and this Fastboot implementation. Do not retry `fetch` or infer that the command is generally safe on another bootloader from the host help text alone.

### Sony Companion installer authenticity check — 2026-10-14

The local `/tmp/Xperia_Companion.exe` candidate was checked offline with `osslsigncode 2.8` and the host's CA store. SHA-256 is `17dabeaae83f7b68e8a20a9678619637bce5b1efb0645d09b894e986bb082dda`; Authenticode file digest matched, certificate chain and timestamp verified, and the tool reported one verified signature. The signer is Sony Nordic (Sweden), with a DigiCert Trusted G4 Code Signing chain; the authenticated description is `Xperia Companion Setup`, and its signed URL metadata points to `https://app.swup.update.sony.net/xperia-companion-links/support`. This authenticates the installer publisher/signature, not its current repair-server behavior, Linux/Wine compatibility, or eligibility for this unlocked E2003.

The installer has not been executed or installed during this check, and the phone was not connected to it. The meaningful next step remains running Sony Companion on a supported Windows/macOS host, selecting the exact E2003 repair flow, and stopping before the final action that starts repair. No repair or data-erasing operation is authorized here. This strengthens confidence in the official preflight software source but does **not** establish a restore path or increase the safe end-to-end ROM estimate yet.

### Wine USB enumeration capability — host-only check — 2026-10-14

The development host has Wine 9.0; its existing Wine prefix contains `wineusb.sys` and a `wineusb` service registration. The connected Sony handset appears in Wine's `HKLM\System\CurrentControlSet\Enum\USB` tree under VID/PID `0FCE:51CB` (the instance identifier/serial is intentionally not recorded here). This proves Wine's USB layer enumerates the handset, but it does **not** prove Xperia Companion can communicate with it or offer repair. Companion has not been installed/launched in Wine, and its installer EULA has not been accepted by the agent. A supported Windows/macOS check remains the authoritative route; a Wine trial would be experimental and must stop before starting software repair.

### Additional exact-model/build mirror lead — 2026-10-14

A public XperiaStockROM page links a Google Drive archive whose central directory names an E2003 `25.0.A.2.31` FTF with CDA `1293-9486` / revision R3A. We verified the outer archive's ZIP metadata by byte range only; the 1.296-GB inner FTF payload has not been retrieved, its CRC has not been checked, and it is not the handset's `1293-7358 R7A` CDA. It is a more closely matched candidate than an E2006 package, but remains a third-party mirror and cannot yet serve as a verified restore route. See [FIRMWARE_SOURCES.md](FIRMWARE_SOURCES.md).

**Readiness effect: still unchanged.** We have a credible same-model/same-build-family firmware lead that could become a fallback stock source after full hash/metadata review, but it provides no current rollback guarantee and no verified exact-CDA base. No bulk payload download or flash was attempted.
