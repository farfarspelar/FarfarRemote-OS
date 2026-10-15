# FarfarOS v0.1 system-only experiment proposal

**Status: PREPARED — NOT AUTHORIZED OR EXECUTED**

This proposal covers one possible write experiment after read-only preflight. It is not a recovery plan. The FarfarOS system image is an offline ext4 POC and has not been boot-tested.

## Candidate artifact

- File: `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4`
- Size: `2,097,152,000` bytes
- SHA-256: `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`
- Format: raw ext4 filesystem image
- Offline validation: APK and boot-animation readbacks passed; `e2fsck -fn` passed; same bytes as two prior reproducible outputs.

The image was reconstructed from the captured E2003 R7A `/system` file tree and metadata, using the inspected R10A ext4 image only as a filesystem container. The build preserves the captured R7A tree and injects FarfarRemote OS. It is not a Sony-signed SIN or a complete firmware package.

## Proposed scope

If, and only if, separately authorized after preflight, the candidate operation would write **only** the `system` partition, expected from the historical read-only E2003 map to be `/dev/block/mmcblk0p19`. The raw image size exactly matches the last observed system partition capacity of 2,097,152,000 bytes.

No boot, fotakernel, recovery, cache, userdata, loader, preloader, logo, TA, NVRAM, calibration, or security partition is in scope. No wipe or relock is part of this proposal.

Candidate command, **shown for review only and not run** (Linux Mint Fastboot 34.0.4 does not accept `-i`; the device is selected by requiring exactly one Fastboot target and verifying its product before any separate authorization):

```sh
fastboot flash system \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4
```

## Evidence and unknowns

- **VERIFIED, historical read-only observations:** handset product E2003; bootloader string `1290-9780 S1_Boot_MT6732_TC9PRA_9`; Android build `25.0.A.2.31`; customization R7A; system alias mapped to `mmcblk0p19`; reported system capacity `2,097,152,000` bytes.
- **REPORTED, superseded:** owner previously said the bootloader is unlocked.
- **VERIFIED, pre-unlock Service Menu:** `Bootloader unlock allowed: Yes`, but not `Bootloader unlocked: Yes`; Fastboot `getvar unlocked` returned no value. `secure: yes` does not prove lock state. The owner later authorized the unlock command and subsequently confirmed `Bootloader unlocked: Yes` in the Service Menu. ADB is available again. No ROM image was flashed.
- **Interpretation of `secure`:** AOSP Fastboot protocol documentation defines `secure` as whether the bootloader requires signed images for install/boot; it is not, by itself, a locked/unlocked state field. Therefore `secure: yes` is recorded but is not used to infer the current lock state. See the [AOSP Fastboot protocol](https://android.googlesource.com/platform/system/core/+/09fe163be2a3f59dfcc34d473b898e777c0f4514/fastboot/README.md).
- **UNKNOWN:** whether this S1 bootloader accepts the `system` Fastboot partition alias and raw ext4 payload. Flashtool's public source has a generic `fastboot flash system <image>` operation, but does not establish E2003 bootloader acceptance. See the pinned [Flashtool implementation](https://github.com/Androxyde/Flashtool/blob/7529dce9a1ffb81e365ba1d7e15f6773463ffd7a/Flashtool/src/main/java/org/flashtool/jna/adb/FastbootUtility.java).
- **UNKNOWN:** whether first boot will complete with the stock R7A boot/FOTA and this reconstructed system. No test of this system image has occurred on hardware.
- **INCONCLUSIVE prior observation:** a separate `fastboot boot` Android-container POC transferred, then USB disconnected with `Status read failed`; no boot result was observable. That experiment did not write the system partition and does not validate this image.

## Backup and recovery position

- A complete raw backup of the live R7A `system` partition is **not available**. A matching file tree/metadata capture exists, and the R10A container plus generated ext4 images are retained, but these are not byte-for-byte backups of the live partition.
- A separate offline R7A stock-file-content reconstruction now exists at `/tmp/FarfarOS-E2003-R7A-stock-tree-reconstruction-v0.1.ext4` (2,097,152,000 bytes; SHA-256 `9942db8cdc048ff7ba9522160c1bf8aba3dcb6e6ce5e1c910f444bbed53880dd`). It removes the injected system APK, restores the captured R7A boot animation byte-for-byte, and passes `e2fsck -fn`. It is not a raw partition backup, a signed Sony package, or a device-tested recovery image; details are in [`RESTORE_RECONSTRUCTION.md`](RESTORE_RECONSTRUCTION.md).
- Exact R7A stock firmware restoration has **not** been verified.
- Sony S1 service/Flashmode transport was observed previously, but no exact R7A repair package or successful restore procedure was verified.
- A historical E2003 TWRP image passed static checks but was built/reported for R5A and has not been boot-tested on this R7A handset.
- Therefore recovery from a failed system-only experiment is **not guaranteed**. A soft brick/boot loop may require a service repair route that is currently unverified.
- **Host-side limitation:** the `/mnt/data` ext4 volume's `jbd2/mmcblk0p1` journal thread is in long-running uninterruptible sleep, and a write attempt there stalled. The validated fallback currently resides on `/tmp` on the separate SSD. Treat the stalled `/mnt/data` output as incomplete and unusable unless it later passes independent checks. See [`RESTORE_RECONSTRUCTION.md`](RESTORE_RECONSTRUCTION.md).

## Required read-only preflight before considering authorization

### Fresh Fastboot/image audit — 2026-10-15

The attached handset was moved from Android to Fastboot for read-only queries,
then returned to Android; ADB is online again. Fastboot 34.0.4-debian reports
product `E2003`, bootloader
`1290-9780 S1_Boot_MT6732_TC9PRA_9`, `secure: yes`, system partition size
`0x7d000000` (2,097,152,000 bytes), and system type `ext4`. The `unlocked`
getvar is empty, and `fastboot oem device-info` returns `unknown command`.
Sony's Service Menu `Service info > Configuration > Rooting Status` reports
`Bootloader unlock allowed: Yes`. This means the device is eligible for an
unlock operation; it is **not** evidence that it has already been unlocked.
Thus the owner's unlocked report is **REPORTED**, but current unlock state
remains **UNKNOWN**. The official Sony procedure uses that menu to check
whether unlocking is allowed, then separately runs the unlock command; see
[Sony's Open Devices guide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader).

The corrected read-only helper was then run against this live Fastboot session.
Image size/hash/type, unique target, E2003 product, exact system partition
capacity and bootloader identifier all passed; it stopped at the unlock check
because the bootloader returns no value. It exited with `PREFLIGHT FAIL` and
issued no write command. The phone was returned to Android and ADB was
confirmed online.

A final standard Fastboot check also tried `fastboot flashing get_unlock_ability`.
This S1 bootloader replied `unknown command`; `getvar unlocked` remained empty
and `getvar secure` returned `yes`. The handset was rebooted back to Android
and ADB returned to `device`. No OEM unlock or write command was sent. This
adds no current unlock-state evidence; Sony's Service Menu still proves only
unlock eligibility.

A final `fastboot getvar all` query was also captured locally and filtered so
that device-specific serial/identity fields were not displayed or recorded.
It returned the same product, bootloader, `secure: yes`, system size and
system type, but no `unlocked`, `locked`, or `lockstate` variable. The device
was returned to Android and ADB was confirmed online. This closes the
available standard Fastboot read-only variable check; it does not prove that
the bootloader is locked, only that its state remains unknown through this
interface.

The locally inspected Flashtool source contains a loader `CMD01` property
query that can report `ROOTING_STATUS` after establishing a Sony S1 loader
session. That is a service/loader protocol operation, not a documented
standalone status query for this exact E2003 firmware. The repository audit
found no validated, non-mutating E2003-specific procedure that uses it to
confirm the current Fastboot unlock state. It is therefore not used as a
substitute for the missing Fastboot state, and no Flashtool session was opened
for this check.

An additional firmware-source check found a similarly named
`25.0.A.2.31-R7A-Nextel-PE` package listed under **E2006** on the source page,
not E2003. It is explicitly excluded as a restore candidate. The same page's
E2003 list offers R10A/R3A/R5A/R1A examples, but no exact E2003 R7A package.
This reinforces that the matching CDA restore path is still unavailable; see
the [source index](https://azrom.net/rom-sony-xperia-e4g-e2003-e2006-e2053-ftf-firmware-lock-remove-file/).

The proposed image's SHA-256 and ext4 check were revalidated. The APK extracted
from it is byte-identical to the repository's v0.4.7 OS APK
(`f412e2047daa411270d253b2e6cd8ce7097291e6deccb7e096eef3a6aab0e7bc`). The
currently installed phone app is 0.4.6-rc5 / versionCode 14; its APK and the
image's v0.4.7 / versionCode 15 APK have valid JAR signatures with the same
certificate SHA-256
`63:F9:33:6D:00:38:B8:EB:E9:AC:82:24:F8:86:9E:1F:87:18:28:D8:1B:62:69:37:23:15:CE:05:5C:F6:07:FD`.
This supports the update path but does not constitute an on-device system-app
migration test. No userdata partition is part of the proposed write.

The previous command example used `fastboot -i`, which this actual Linux
Fastboot binary rejects as an invalid option. The reviewed command above and
the preflight script now use standard Linux Fastboot syntax. The first
physical run exposed a second parser assumption (partition size was reported
as hexadecimal without a `0x` prefix); that is corrected and the actual helper
now reaches the unlock-state check. No write command has been run.

With the handset physically present and in Fastboot, the following read-only
queries have now been run:

```sh
fastboot devices
fastboot getvar product
fastboot getvar version-bootloader
fastboot getvar secure
fastboot getvar unlocked
fastboot getvar partition-size:system
fastboot getvar all
```

The `getvar all` output was filtered locally; no serial or device identity
number was retained in the report. Neither `unlocked`, `locked`, nor
`lockstate` was returned.

The read-only helper [`../tools/preflight_e2003_system_write.sh`](../tools/preflight_e2003_system_write.sh) checks the local image size/hash/type, exactly one Fastboot device, exact product, system partition size, bootloader identifier, and a positively reported unlocked state. It does not print the USB serial and never runs a write, boot, erase, or reboot command. Its output must say `READ-ONLY PREFLIGHT PASSED`; any unavailable or mismatched value stops the process. Re-check the image size and SHA-256 immediately before any separately approved write.

## Expected outcomes and failure modes

1. **Fastboot rejects the alias/image before writing:** no successful installation is established; capture output and stop. Do not try guessed aliases.
2. **Write reports success but Android fails to boot:** likely system/boot/framework mismatch or damaged filesystem; do not wipe userdata or write another partition as an improvised fix.
3. **Android boots:** verify build identity, HOME launcher, touchscreen/display, Settings/input, Wi-Fi reconnect, Kodi discovery/manual connection, audio/subtitle selection, USB/ADB, charging/battery reporting, and reboot before considering the experiment successful.
4. **USB disconnects or the result is ambiguous:** treat status as unknown; do not repeat the write. Observe USB mode and use only the separately reviewed recovery route.

## Authorization boundary

No write command has been issued under this proposal. Running the candidate `fastboot flash system` command requires a separate explicit approval naming this exact image, SHA-256, and the `system` partition after the read-only preflight is available. Broad approval to continue ROM research is not treated as approval for this particular partition write.

## Bootloader unlock addendum — 2026-10-15

The separate bootloader unlock was explicitly authorized and completed as a
command attempt. Fastboot returned `OKAY` for one `oem unlock` command, then
`fastboot reboot` returned `OKAY`. The phone enumerates as Android USB, but no
authorized ADB device has appeared yet; verification of `Bootloader unlocked:
Yes` remains pending. This does not alter the authorization boundary above:
the proposed `system` partition write has not been authorized or executed.
