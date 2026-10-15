# FarfarOS Experimental v0.1 build report

## Bootloader status addendum — 2026-10-15

The Service Menu on the exact E2003 later showed `Bootloader unlock allowed:
Yes`, but not `Bootloader unlocked: Yes`; Fastboot's `getvar unlocked` remains
blank. Thus previous build-report statements that merely say the owner-reported
unlocked status was unconfirmed are superseded: current read-only evidence
verifies eligibility to unlock, not that unlocking has occurred. The offline
system-image build results below are unaffected; no image was flashed and no
partition was written. A flash trial remains blocked pending separately
authorized unlock if needed and a validated restore path. Sony's official
unlock guide states unlocking factory-resets user data, does not grant root,
and prevents restoration of DRM keys: [Sony Open Devices — unlock bootloader](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader).

## Follow-up artifact audit — 2026-10-15

The retained data-volume image was independently rechecked after the later
kernel/boot-container work. The raw image
`/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4`
is 2,097,152,000 bytes and has SHA-256
`cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`.
`file` identifies it as ext4 and a fresh read-only `e2fsck -fn` completed all
five passes successfully. `debugfs` readback confirmed `/app/FarfarRemote.apk`
is a root-owned `0644` regular file with `u:object_r:system_file:s0`; its
readback hash `f412e2047daa411270d253b2e6cd8ce7097291e6deccb7e096eef3a6aab0e7bc`
matches the retained v0.4.7 OS APK byte-for-byte. Its signer certificate SHA-256
matches the certificate pinned by the builder. The boot-animation readback also
matches the project asset hash `543682f34508e7031c5da63898285f86cf72bbcd98b572c859204f4502131eef`,
and `unzip -t` passes.

The sparse companion remains a packaging experiment only; its SHA-256 is
`81b9e117d3832033e520059e8834f6084b4bef05b290258286c5aa6c41dfb4`. The separate
callass kernel boot-container candidate remains
`80d51e07d4f5d7151cc7899833aed246539c23ab306412169c622390509d8182` and parses
as an Android boot image, but combines the rebuilt kernel with a non-R7A-matched
community ramdisk. Neither container is proven acceptable to this bootloader or
compatible with the live device. This audit did not build a new ROM or access
device partitions. At audit time both `adb devices` and `fastboot devices` had
no attached target, so boot, Wi-Fi, touch, charging, HOME and Kodi behavior of
these artifacts remain unverified on hardware.

A fresh comparison against the private, device-captured R7A metadata manifest
then checked all 4,447 original `/system` paths in the built image. Type, mode,
UID, GID, SELinux label and symlink target all matched (zero mismatches). A
full readback/hash comparison matched 4,192 of 4,193 original regular files;
the sole difference was `/media/bootanimation.zip`, intentionally replaced
with the supplied FarfarOS animation and separately verified byte-for-byte.
The inserted `/app/FarfarRemote.apk` is an additional file outside that stock
manifest and was separately verified against the original APK. This strengthens
the local content-integrity result; it does not establish bootability or
firmware-package compatibility.

## Boot ramdisk and kernel-module gate — 2026-10-15

An offline review of the R10A ROOTFS ramdisk used by the Android boot-container
candidate found `/dev/block/platform/mtk-msdc.0/by-name` mounts for `system`,
`userdata`, `cache`, `protect1` and `protect2`. Its fstab marks both `protect1`
and `protect2` `wait,check,autoformat`. These are separate device partitions
that the project partition map identifies as protected. The exact trigger
conditions and consequences of `autoformat` have not been experimentally
established; therefore this boot candidate must not be used for another
start-attempt as-is. A same-build, R7A-matched ramdisk is still unavailable.
Any locally prepared alternative must first be statically reviewed to prove
that its startup path cannot format `protect1`/`protect2`, NVRAM, calibration,
or other unrelated partitions. This is a boot-candidate gate, not a problem in
the already-built `/system` filesystem image.

The init imports add further unverified side effects: Sony bootstrap imports
`init.sony-bootstrap-wipedata.rc` and `init.sony-bootstrap-mr.rc` on `fs`, and
starts `updatemiscta` on `early-boot`. Static inspection of the matching R7A
system binaries found `miscta_write_unit` plus `TA_WIPE_DATA` strings in
`wipedata` (SHA-256 `0cb41a043e06e3b2dd8aaa1084e0f29ebd22b09d3293521181c459b722d3363e`),
`miscta_write_unit_critical` plus `TA_MASTER_RESET` and wipe/format strings in
`mr` (SHA-256 `def38b1624bdec041ad8788495d648d585c3004ae81b812e14a5417f941d7221`),
and TA write API references in `updatemiscta` (SHA-256
`611646c579c537001d8fcc592f44bb2f4428a0f6c754f2d4dd0793a10b35eda4`). The
functions' exact runtime guards and behavior on this phone are not established
by static strings. Because this ramdisk is not the live R7A boot capture, none
of those side effects can be assumed benign. The offline diagnostic variant
omits those explicit init actions and both protect-partition fstab rows; its
static scan verifies no other `.rc` file starts or execs those named actions.
It still is not safe or validated to boot: other platform services may depend
on the omitted Sony setup, and runtime behavior is unknown.

The rebuilt callass kernel configuration has `CONFIG_MODULES=y`, but its saved
build output contains zero `.ko` files. The R7A capture lists an empty
`/system/lib/modules` directory. This is consistent with a build where the
needed drivers are built in, but does not prove that the rebuilt kernel has the
exact R7A hardware configuration. The kernel version string is `3.10.48`,
while the live kernel reports `3.10.48+`; source/config identity and hardware
driver behavior remain unverified.

## Physical-device connection restored — 2026-10-15

After the owner started the handset normally, read-only ADB again verified
E2003 / Android 4.4.4 API 19 / build `25.0.A.2.31` / CDA `1293-7358 R7A`.
Fastboot is not connected; the phone is in Android. `/proc/version` reports
Linux `3.10.48+`, and all four CPU cores were online in this snapshot. `wlan0`
is bound to `mt-wifi`, the live input devices expose the expected 540×960 touch
coordinates and physical keys, and `/proc/modules` is empty. These are fresh
stock-runtime references, not experimental-ROM results.

An ordinary ADB-shell `id` remains UID 2000; `ro.secure=1`, `ro.debuggable=0`,
and common `su` locations are absent. A guarded read of at most four bytes from
each `boot` and `fotakernel` block path was denied by Android permissions; no
partition bytes were saved. This confirms that the missing exact boot payload
cannot be recovered through the current normal ADB session. The private
read-only capture remains outside Git. No reboot, setting change, root attempt,
or device write was performed during this checkpoint.

To support offline experimentation without those specific automatic actions,
`tools/make_e2003_boot_candidate_nonformatting.py` now creates a separate
candidate from the pinned kernel container. The output
`/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-callass-kernel-boot-candidate-no-protect-mounts-no-bootstrap-v0.1-rerun.img`
is 8,957,952 bytes, SHA-256
`fde40f857262b04a48d98662069c2e3e134ad6330cb288f6894df55a9f79cbfb`.
It retains the kernel byte-for-byte, removes the two protect-partition fstab
rows and empties the automatic wipe/reset/MiscTA-update action files. A full
Android-header + MediaTek-wrapper + gzip/cpio parse passed; all non-target
ramdisk files compare byte-for-byte, and a repeat build produced the same hash.
The script also refused output in the repository and on `/tmp`. This is a
**modified diagnostic artifact only**: skipping Sony bootstrap work and
protect mounts may prevent Android startup or break required device behavior.
It is not authorized or validated for a phone boot attempt and is not flashable.

## Status

## Boot-startup side-effect audit — 2026-10-15

The diagnostic Android boot-container candidate was parsed offline and its
ramdisk `fstab` plus all init `.rc` files were scanned for block-device paths,
format/wipe commands, and Sony bootstrap actions. The already documented
`protect1`/`protect2` autoformat rows and named wipe/reset/MiscTA bootstrap
actions are absent from this diagnostic variant. This narrows those specific
known hazards; it does **not** prove the remaining init sequence is safe or
will boot.

The scan also confirms that the retained MediaTek init script runs `e2fsck`
and `tune2fs -O has_journal` on the separate `apps_log` partition during its
filesystem setup. That is an intentional on-device filesystem mutation and
has not been tested with this image. The R7A system image does not contain
`/system/etc/install-recovery.sh`, although the candidate's generic init
script declares a `flash_recovery` service pointing to that path; the service
therefore has no corresponding helper in this built system image. Static
absence is not runtime proof that recovery will remain untouched, especially
because the boot ramdisk and partition alias behavior are not matched to live
R7A. No init rules, partitions, or phone state were changed during this audit.

The audit used local retained artifacts and read-only host parsers only. It
does not clear the boot test gate: the candidate is still based on an R10A
ramdisk, and no exact R7A boot/fotakernel image or proven restore route exists.

## Read-only artifact recheck — 2026-10-15

The primary R7A-derived `/system` image was rehashed from the data volume and
again passed all five passes of `e2fsck -fn`: SHA-256
`cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`.
The separate stock-file-content fallback on the host SSD was also rehashed and
passed `e2fsck -fn`: SHA-256
`9942db8cdc048ff7ba9522160c1bf8aba3dcb6e6ce5e1c910f444bbed53880dd`.
This is repeatable host-side file integrity evidence only. The stock-file
fallback is not a raw partition backup, and neither image has been accepted
or boot-tested by the E2003 S1 bootloader. No device partition was read or
written during this recheck.

### apps_log-free diagnostic container

To remove the newly identified `apps_log` filesystem operations from the
static candidate, [`../tools/make_e2003_boot_candidate_skip_apps_log.py`](../tools/make_e2003_boot_candidate_skip_apps_log.py)
now accepts only the pinned diagnostic input hash and removes the complete
`#mount apps_log block` from `init.mt6752.rc`. It verifies the cpio round-trip,
asserts no init `.rc` file retains `apps_log` or `/mnt/idd` references, and
preserves the kernel payload byte-for-byte. The script was syntax-checked and
run against the retained candidate; the output parses as an Android legacy
boot-container and has SHA-256
`c10a124cc63053046a7a24e1df69df30de597229d94ec2fca109b13417a49d76`.

The 8,957,952-byte artifact is stored outside Git at
`/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-callass-kernel-boot-candidate-no-apps-log-v0.1.img`.
This removes the explicit `apps_log` check/tune/mount block, but can break Sony
logging or other undocumented dependencies. It still uses the non-R7A R10A
ramdisk, borrowed Android boot-image header geometry, and a rebuilt kernel
whose config is not proven identical to R7A. It remains a **static diagnostic
artifact only**, not a bootable/flashable image or permission to test on the
phone.

The first combined offline build completed on 2026-10-15. Proprietary-derived images are stored outside Git on `/mnt/data`; legacy `/tmp` paths are symlinks to the retained artifacts.

| Gate | Result |
|---|---|
| Source R10A image SHA pinned | **PASS** — `931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949` |
| FarfarRemote APK package/min API/signature | **PASS** — `org.farfarremote`, version 0.4.7, min API 19; existing device signer accepted |
| HOME launcher declaration | **PASS (static)** — APK manifest contains MAIN + HOME + DEFAULT |
| Boot animation archive/frames | **PASS (static)** — ZIP CRC valid, expected intro/loop entries, descriptor and all frames are 540×960 |
| R7A file/metadata reconstruction | **PASS** — 2 R7A-only files added, 17 R10A-only paths removed, 15 files replaced |
| Combined ext4 build | **PASS** — `/tmp/FarfarOS-E2003-R7A-v0.1-system.ext4` |
| System image SHA-256 | `98a7461bc9374c90016e82ce01702454b57f4c5a46795a99bfbcccd9a72e8651` |
| Filesystem check and payload readback | **PASS** — `e2fsck -fn` exit 0; APK and boot animation readback hashes matched inputs |
| Independent image inspection | **PASS (static)** — ext4, clean state; 512,000 blocks × 4,096 bytes; 78,887 free blocks |
| System build properties | **PASS (static)** — E2003, Android 4.4.4, API 19, `25.0.A.2.31` |
| Sony SIN/FTF packaging | Not implemented |
| Boot image matched to R7A | Not implemented |
| Hardware boot test | Not performed |
| Device write | Not performed |

The APK input SHA-256 is `f412e2047daa411270d253b2e6cd8ce7097291e6deccb7e096eef3a6aab0e7bc`; boot animation SHA-256 is `543682f34508e7031c5da63898285f86cf72bbcd98b572c859204f4502131eef`. The checksum sidecar is `/tmp/FarfarOS-E2003-R7A-v0.1-system.ext4.sha256`.

**Interpretation:** this is a successfully built and filesystem-validated experimental `/system` partition image. It is not a complete ROM, not packaged for Sony flashing, not proven boot-compatible, and not boot-tested. Do not flash based on this report alone. Neither a boot image nor recovery path was changed or generated by the combined build.

## Rebuild check — 2026-10-15

The checked-in build script was rerun from the same local input set and the published v0.4.7 OS APK. The rebuild completed, `e2fsck -fn` passed, and the builder again verified the R10A input, APK, animation, and payload readbacks. The resulting image was 2,097,152,000 bytes with SHA-256 `558f52709d3839d883296cdd70d8032c44ae7af50d79893948e101d4084af021`, so it is **not byte-identical** to the earlier image (`98a7461b…`). Both images report the same ext4 UUID, feature set, inode/block counts, and free-block/inode counts; the observed superblock `Last write time` differs (`11:24:00` vs `11:53:54` UTC). This confirms the current builder is repeatable in filesystem/payload validation, but not byte-for-byte deterministic. It does not establish that every filesystem metadata byte is identical.

The historical rebuild path was `/tmp`; its firmware-derived image and checksum were retained during the disk migration and are not committed. It is not flashable or boot-tested. On the live device, ordinary ADB shell also failed the bounded read probe for both boot and fotakernel due to permissions; see [recovery notes](../RECOVERY_STRATEGY.md).

## Reproducible rebuild check — 2026-10-15

The builder now pins ext4 timestamps using `SOURCE_DATE_EPOCH` (default `1704067200`), `E2FSPROGS_FAKE_TIME`, and `E2FSCK_TIME`. Two independent full builds with the same R10A container/tree, captured E2003 R7A tree/metadata, v0.4.7 OS APK, and boot animation produced byte-identical images:

| Output | Size | SHA-256 | Validation |
|---|---:|---|---|
| `FarfarOS-R7A-repro-1.ext4` | 2,097,152,000 bytes | `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d` | Payload readback and `e2fsck -fn` passed |
| `FarfarOS-R7A-repro-2.ext4` | 2,097,152,000 bytes | `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d` | Payload readback and `e2fsck -fn` passed |

Both outputs are stored outside the repository under `/mnt/data/FarfarRemote-Research-POC/`; no proprietary-derived image was added to Git. This proves byte-for-byte repeatability for the tested local inputs and e2fsprogs 1.47.0 host, not portability to every host. The result remains an ext4 `/system` POC only: it is not a complete Sony firmware package and has not been booted.

## Data-volume rebuild after disk migration — 2026-10-15

The root filesystem was full before the storage work (507 MiB available, 100% used). We moved 151 FarfarOS-related `/tmp` entries (about 25 GiB) and the 962 MiB Gradle cache to `/mnt/data`. No files were deleted; old `/tmp` names remain as symlinks to the preserved targets. Root now has about 26 GiB available (77% used). Unrelated caches were left untouched. A name manifest is stored beside the migrated files.

The updated wrapper was used to build a separate output at `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4`. The wrapper directed `TMPDIR`, `TEMP`, and `TMP` to the data volume and rejected an attempted output path under `/tmp` before invoking the builder. A follow-up guard now also refuses to start unless output and temporary paths resolve to a filesystem distinct from `/` with at least 5 GiB free; this avoids a silent fallback if `/mnt/data` is unmounted.

The build completed with payload readback and `e2fsck -fn` passing. It produced a 2,097,152,000-byte ext4 image with SHA-256 `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`, byte-identical to both prior reproducible outputs. This confirms the new storage path for this build and input set. It remains an offline partition-image POC: not a complete or flashable Sony ROM, and not hardware-booted. The output and all proprietary inputs remain outside Git.

## Candidate system-only installation path — 2026-10-15

The preserved Flashtool source was inspected at commit `7529dce9a1ffb81e365ba1d7e15f6773463ffd7a`. Its generic Fastboot utility constructs `fastboot flash system <image>`, which is a possible route for a raw ext4 system image. This is software-source evidence only; it does not prove that the E2003 S1 bootloader accepts the `system` alias or this payload. The Flashtool “Create SIN As” UI is restricted to SIN v1/YAFFS2 and cannot produce a valid Sony SIN v3 image for this ext4 system. No custom SIN was fabricated.

A separate system-only proposal is prepared in [`FLASH_EXPERIMENT_PROPOSAL.md`](FLASH_EXPERIMENT_PROPOSAL.md), including the exact artifact/hash, target/capacity evidence, read-only preflight, failure modes, and current recovery limitations. No flash command was issued. The handset is not presently visible to ADB or Fastboot, the reported unlock state is not independently confirmed, no raw live R7A system backup exists, and exact-R7A restoration is unverified. Any write still requires fresh preflight and separate explicit approval for this exact artifact and partition.

The read-only helper [`../tools/preflight_e2003_system_write.sh`](../tools/preflight_e2003_system_write.sh) now checks the candidate image, one connected target, E2003 product, exact system size, expected S1 bootloader identifier, and a positive unlocked response. It discloses no device serial and contains no write/reboot subcommand. Mocked Fastboot tests passed for a valid result and refusals on model, capacity, bootloader, unlock, and multiple-device mismatches; physical-device behavior remains untested.

The image length also exactly matches the live handset's reported `system` partition capacity: `2,097,152,000` bytes (`2,048,000` 1-KiB blocks). This closes only the raw size-fit check. It does not establish an accepted Sony image container, safe write path, boot-chain compatibility, or successful hardware boot; see [HARDWARE_COMPATIBILITY.md](HARDWARE_COMPATIBILITY.md) and [partition layout](../PARTITION_LAYOUT.md).

## Separate boot-container experiment

A separate offline Android boot-image **container POC** exists at `/tmp/farfar-e2003-boot-poc-verify2.img` (8,445,952 bytes; SHA-256 `1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`). Static parsing confirms `ANDROID!`, 2,048-byte pages, the expected legacy E2003 address fields, and the MediaTek command line. Its kernel and ROOTFS payloads come from community-mirrored E2003 R3A/R10A `25.0.A.2.31` files; the Android boot header geometry comes from an unaudited historical E2003 R5A TWRP image. Although the kernel/ramdisk hashes cross-match between those two stock candidates, neither payload/header provenance is an authenticated live-R7A boot capture. It is not a Sony ELF, not R7A-matched, not combined with the system image, and not boot-tested. It must not be called a valid boot partition image or flashed. The static POC and its limitations are documented in [`repack_e2003_stock_boot_poc.py`](../tools/repack_e2003_stock_boot_poc.py) and [`RECOVERY_STRATEGY.md`](../RECOVERY_STRATEGY.md).

## Sony ELF structure follow-up — 2026-10-15

Recovery image availability is no longer being treated as a prerequisite for offline ROM engineering. The R10A and R3A E2003 `25.0.A.2.31` FTFs were independently extracted with embedded SIN payload hash validation. Their `boot.elf` files are exactly byte-identical (8,447,047 bytes; SHA-256 `a37587ac9a7166ff2ed32ac6e32744af058fff66b1ef67f43d644c21ddaa3217`). A new read-only tool, [`inspect_e2003_sony_boot_elf.py`](../tools/inspect_e2003_sony_boot_elf.py), validated the 32-bit ARM ELF and two load segments: raw MediaTek `KERNEL` wrapper at `0x40008000` (wrapper SHA-256 `4115fd4775103d21c622abf22b27e260100d005aa5f5b22ed1fd9dfc183e0d36`) and gzip-compressed `ROOTFS` cpio wrapper at `0x44000000` (wrapper SHA-256 `ddd9513e14c700433b2b3a36af94cd7e91b82a3895829cb8b5816410ac321152`). The tool also confirmed that the rootfs contains `init.rc`, `default.prop`, and `fstab`. R10A and R3A `fotakernel.elf` are also byte-identical to each other, sharing the kernel wrapper but containing a different FOTA rootfs.

This is stronger cross-source evidence for the shared E2003/build-family boot payloads, and corrects older notes that incorrectly described the kernel segment as gzip-compressed. It remains **candidate-only**: neither archive is authenticated by Sony or matches the live CDA `1293-7358 R7A`. The ELF segment structure is not yet mapped to the bootloader's exact accepted partition format. The existing Android `boot.img` container POC still depends on unaudited TWRP header geometry and is neither boot-tested nor suitable to label flashable. No device partition was read or written during this work.

## Live launcher state check — 2026-10-15

The attached phone was queried read-only over ADB. Identity matched E2003 / Android 4.4.4 / build `25.0.A.2.31` / CDA `1293-7358 R7A`. `dumpsys package` showed `org.farfarremote/.MainActivity` as the persisted preferred HOME activity (`mAlways=true`), selected among FarfarRemote and both Sony launcher activities. Installed FarfarRemote is currently a `/data/app` package, version `0.4.6-rc5`. The read-only boot/fotakernel probe again received `Permission denied` for four-byte reads from both partition nodes.

This confirms the working device already stores FarfarRemote's HOME choice in its data state. Preserving `/data` is therefore important to maintain the current startup experience; whether Android 4.4 migrates the existing user-installed package cleanly when an identical signed APK is present in `/system/app` has not been experimentally verified. No package, preference, partition, or system setting was changed.

## Temporary boot attempt — 2026-10-15

With the owner authorizing continued experiments, the 8,445,952-byte Android boot-container POC (`1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`) was sent using `fastboot boot`, not `fastboot flash`. The host reported the image transfer as `OKAY` (8,248 KB), then the boot command ended with `FAILED (Status read failed (No such device))`. USB re-enumerated as Sony USB product `0fce:e1cb` with a mass-storage-only interface; neither ADB nor Fastboot became available during the observation window. Because the host could not observe Android boot completion or read a post-boot fingerprint, this is **INCONCLUSIVE**: it does not prove either boot success or boot failure. No partition was written, erased, unlocked, or wiped by the commands issued.

To regain the normal diagnostic path, the phone may need a physical long-press power cycle; once ADB returns, verify the stock fingerprint and repeat read-only checks. Do not infer the temporary boot's outcome from USB re-enumeration alone. The exact contents of the running screen and system are **UNKNOWN** until a person inspects the handset or ADB returns.

## Existing callass kernel build audit — 2026-10-15

The preserved offline build output was checked against the source mirror at commit `2a84825e8268393267e454e35a00f80d48c58949`. Its build log ends with `Successfully built kernel`; the ELF identifies as 32-bit ARM EABI5 and reports Linux `3.10.48`, matching the live kernel's reported `3.10.48+` version string. The built zImage is 6,839,512 bytes, SHA-256 `640b20b8dc0e74482a9752d473f179030e48ee9efa1512968c5c374481144a45`. It is retained outside Git in the private kernel-source workspace.

Static output confirms `CONFIG_ARCH_MT6752=y`; the generated `callass` project config selects `CUSTOM_KERNEL_TOUCHPANEL = ektf2k S3202`, and the build produced the EKT touch-driver object. The three configured HX8389 LCM candidate objects were also compiled. This corrects the earlier interpretation of live input name `mtk-tpd`: that is the generic MediaTek TPD framework label and does not establish a controller mismatch. The live controller/firmware and which LCM candidate is active are still unknown. Source build success and matching kernel version do not prove that this mirror's configuration is the exact R7A kernel or that its zImage boots on the handset.

## Rebuilt-kernel boot-container candidate — 2026-10-15

Added `research/custom-rom/tools/repack_e2003_kernel_source_boot_candidate.py` and assembled a separate Android legacy boot-image container from the offline `callass` zImage plus the extracted R10A MediaTek ROOTFS ramdisk, using header geometry from the unaudited E2003 R5A recovery reference. The artifact is outside Git at `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-callass-kernel-boot-candidate.img` (8,960,000 bytes; SHA-256 `80d51e07d4f5d7151cc7899833aed246539c23ab306412169c622390509d8182`). `file` recognizes an Android bootimg with 2,048-byte pages; the script validates ARM zImage magic, ramdisk wrapper/cpio structure, header lengths, and payload readback. A second build was byte-identical; a repository-output refusal check passed.

This candidate exists only to support future **temporary boot experimentation** with the rebuilt kernel. It is not the original stock boot image, not built from the live R7A ramdisk, not paired with the FarfarOS system image, not Sony-signed, not hardware-tested, and not established as flashable. Its header is borrowed, its ramdisk is from a different CDA, and the mirror's exact R7A configuration remains unverified. No device command was issued.

At the time of this audit the workstation sees USB VID:PID `0fce:e1cb` with a mass-storage-only interface. Linux enumerates `/dev/sdb` as `SONY Mass Storage`, but the SCSI device reports “Media removed” and zero sectors; there is no readable LUN to inspect. `adb devices` and `fastboot devices` return no target. Host kernel logs also contain an earlier `0fce:0dde` enumeration identified by USB descriptors as `S1boot Fastboot`, but Fastboot is not currently present. The captured R7A `build.prop` advertises `ro.sys.usb.storage.type=mtp,mass_storage`, so the mass-storage-only interface alone cannot establish whether Android finished booting or identify a recovery state. The handset's screen/boot state remains unknown. No USB storage was mounted or written.

## Android sparse container experiment — 2026-10-15

Added `tools/ext4_to_android_sparse.py` to package an existing raw image as a standard Android sparse v1 container without modifying the raw input. It refuses to overwrite an output, requires 4096-byte alignment, emits RAW and DONT_CARE chunks, and records the expanded-image CRC32. The tool routes no data to the phone.

The sparse artifact is outside Git at `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.sparse.img`:

| Artifact | Size | SHA-256 | Validation |
|---|---:|---|---|
| Raw ext4 input | 2,097,152,000 bytes | `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d` | Existing payload readback and `e2fsck -fn` pass |
| Android sparse v1 | 1,729,989,020 bytes | `81b9e117d3832033e520059e8834f6084b4bef05b29025828646c5aa6c41dfb4` | Identified as Android sparse v1; expanded by the locally preserved MediaTek `simg2img`; byte-for-byte `cmp` and SHA-256 match the raw input |

This reduces transfer size by about 17.5%, which is modest. It proves only that the container is structurally readable by the host-side converter and expands to the exact raw image. It does **not** prove the E2003 S1 bootloader accepts this container, that a Sony-valid signed image has been produced, or that the filesystem boots. The inspected MediaTek SignTool contains a sparse-image signing path, but it requires signing configuration and does not establish that this reconstructed `/system` is a valid Sony S1 payload. Do not infer flashability from this experiment.

## Continuation and artifact revalidation — 2026-10-15

KingRoot was skipped by owner decision; no rooting utility was acquired or run. The available handset is in normal Android mode and remains the unmodified R7A control device. The existing offline R7A system image was rechecked: SHA-256 `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`; `e2fsck -fn` completed all five passes. Its sparse companion hash is `81b9e117d3832033e520059e8834f6084b4bef05b29025828646c5aa6c41dfb4`. The diagnostic boot-container hash is `fde40f857262b04a48a98662069c2e3e134ad6330cb288f6894df55a9f79cbfb`; host `file` parses it as an Android boot image. These are offline integrity/format checks only. The system image is not a complete firmware package, and the boot container is not R7A-matched, boot-tested, or approved for installation.

The pinned, clean MTKClient checkout and isolated PyUSB environment are ready for a narrowly scoped attempt to read the live `boot`/`fotakernel` partitions in BootROM mode. The read-only wrapper was not invoked because the phone is currently running Android rather than exposing the expected BootROM USB identity. Exact boot acquisition is now the nearest technical gate; a trustworthy recovery/restore route and a separately reviewed boot test remain unresolved.
