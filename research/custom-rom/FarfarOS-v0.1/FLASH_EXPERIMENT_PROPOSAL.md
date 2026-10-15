# FarfarOS v0.1 system-only experiment record

**Status: SYSTEM WRITE REPORTED OKAY; ANDROID STARTUP NOT OBSERVED**

This record documents the owner-approved write to the E2003 `system` partition and the first startup observation. It is not a recovery plan. The FarfarOS system image remains an experimental ext4 POC and has not reached a verified Android boot on hardware.

## Candidate artifact

- File: `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4`
- Size: `2,097,152,000` bytes
- SHA-256: `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`
- Format: raw ext4 filesystem image
- Offline validation: APK and boot-animation readbacks passed; `e2fsck -fn` passed; same bytes as two prior reproducible outputs.

The image was reconstructed from the captured E2003 R7A `/system` file tree and metadata, using the inspected R10A ext4 image only as a filesystem container. The build preserves the captured R7A tree and injects FarfarRemote OS. It is not a Sony-signed SIN or a complete firmware package.

## Scope performed

After the read-only preflight and the owner’s explicit approval of this exact image/hash/partition, the operation wrote **only** the Fastboot `system` target, mapped by prior read-only evidence to `/dev/block/mmcblk0p19`. No boot, fotakernel, recovery, cache, userdata, loader, preloader, logo, TA, NVRAM, calibration, or security partition was in scope. No wipe or relock was run.

The command that was run (Linux Mint Fastboot 34.0.4; no `-i` option):

```sh
fastboot flash system \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4
```

## Evidence and unknowns

- **VERIFIED, historical read-only observations:** handset product E2003; bootloader string `1290-9780 S1_Boot_MT6732_TC9PRA_9`; Android build `25.0.A.2.31`; customization R7A; system alias mapped to `mmcblk0p19`; reported system capacity `2,097,152,000` bytes.
- **REPORTED, superseded:** owner previously said the bootloader is unlocked.
- **VERIFIED, pre-unlock Service Menu:** `Bootloader unlock allowed: Yes`, but not `Bootloader unlocked: Yes`; Fastboot `getvar unlocked` returned no value. `secure: yes` does not prove lock state. The owner later authorized the unlock command and subsequently confirmed `Bootloader unlocked: Yes` in the Service Menu. ADB was available again before the system trial. No ROM image had been flashed at that checkpoint.
- **Interpretation of `secure`:** AOSP Fastboot protocol documentation defines `secure` as whether the bootloader requires signed images for install/boot; it is not, by itself, a locked/unlocked state field. Therefore `secure: yes` is recorded but is not used to infer the current lock state. See the [AOSP Fastboot protocol](https://android.googlesource.com/platform/system/core/+/09fe163be2a3f59dfcc34d473b898e777c0f4514/fastboot/README.md).
- **VERIFIED, operation result:** the S1 bootloader accepted the `system` alias and raw ext4 payload for transfer/write and returned `OKAY`. **UNKNOWN:** whether all bytes persisted as intended, since no raw partition readback was performed. See the pinned [Flashtool implementation](https://github.com/Androxyde/Flashtool/blob/7529dce9a1ffb81e365ba1d7e15f6773463ffd7a/Flashtool/src/main/java/org/flashtool/jna/adb/FastbootUtility.java).
- **UNKNOWN:** whether Android will complete startup with the stock R7A boot/FOTA and this reconstructed system. The first post-write boot test did not produce ADB/Fastboot; USB exposed only a Sony Mass Storage interface. The screen state was not observed.
- **INCONCLUSIVE prior observation:** a separate `fastboot boot` Android-container POC transferred, then USB disconnected with `Status read failed`; no boot result was observable. That experiment did not write the system partition and does not validate this image.

## Backup and recovery position

- A complete raw backup of the live R7A `system` partition is **not available**. A matching file tree/metadata capture exists, and the R10A container plus generated ext4 images are retained, but these are not byte-for-byte backups of the live partition.
- A separate offline R7A stock-file-content reconstruction now exists at `/tmp/FarfarOS-E2003-R7A-stock-tree-reconstruction-v0.1.ext4` (2,097,152,000 bytes; SHA-256 `9942db8cdc048ff7ba9522160c1bf8aba3dcb6e6ce5e1c910f444bbed53880dd`). It removes the injected system APK, restores the captured R7A boot animation byte-for-byte, and passes `e2fsck -fn`. It is not a raw partition backup, a signed Sony package, or a device-tested recovery image; details are in [`RESTORE_RECONSTRUCTION.md`](RESTORE_RECONSTRUCTION.md).
- Exact R7A stock firmware restoration has **not** been verified.
- Sony S1 service/Flashmode transport was observed previously, but no exact R7A repair package or successful restore procedure was verified.
- A historical E2003 TWRP image passed static checks but was built/reported for R5A and has not been boot-tested on this R7A handset.
- Therefore recovery from a failed system-only experiment is **not guaranteed**. A soft brick/boot loop may require a service repair route that is currently unverified.
- **Host-side limitation:** the `/mnt/data` ext4 volume's `jbd2/mmcblk0p1` journal thread is in long-running uninterruptible sleep, and a write attempt there stalled. The validated fallback currently resides on `/tmp` on the separate SSD. Treat the stalled `/mnt/data` output as incomplete and unusable unless it later passes independent checks. See [`RESTORE_RECONSTRUCTION.md`](RESTORE_RECONSTRUCTION.md).

## Read-only Fastboot preflight history

### Fresh Fastboot/image audit — 2026-10-15

The attached handset was moved from Android to Fastboot for read-only queries,
then returned to Android; ADB is online again. Fastboot 34.0.4-debian reports
product `E2003`, bootloader
`1290-9780 S1_Boot_MT6732_TC9PRA_9`, `secure: yes`, system partition size
`0x7d000000` (2,097,152,000 bytes), and system type `ext4`. The `unlocked`
getvar is empty, and `fastboot oem device-info` returns `unknown command`. At
that time the Service Menu showed `Bootloader unlock allowed: Yes`, which
indicated eligibility only. The owner later authorized and completed the Sony
unlock operation and confirmed `Bootloader unlocked: Yes` in the Service Menu.
The official Sony procedure distinguishes eligibility from current state; see
[Sony's Open Devices guide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader).

The corrected read-only helper was then run against this live Fastboot session.
Image size/hash/type, unique target, E2003 product, exact system partition
capacity and bootloader identifier all passed; it stopped at the unlock check
because the bootloader returns no value. At that earlier checkpoint it exited with `PREFLIGHT FAIL` and
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
reached the unlock-state check at that historical checkpoint. No write command had been run yet.

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

The read-only helper [`../tools/preflight_e2003_system_write.sh`](../tools/preflight_e2003_system_write.sh) checks the candidate image, one connected target, E2003 product, exact system size, and expected S1 bootloader identifier. This bootloader returns an empty `getvar unlocked` even though the owner confirmed the Service Menu says unlocked; the helper now requires an interactive exact-phrase confirmation in that case and fails closed for non-interactive calls. It discloses no device serial and contains no write/reboot subcommand. A mocked Fastboot run passed with the exact owner-confirmation phrase; a non-interactive run correctly failed closed. The subsequent physical preflight on the E2003 passed, as recorded below.

## Expected outcomes and failure modes

1. **Fastboot rejects the alias/image before writing:** no successful installation is established; capture output and stop. Do not try guessed aliases.
2. **Write reports success but Android fails to boot:** likely system/boot/framework mismatch or damaged filesystem; do not wipe userdata or write another partition as an improvised fix.
3. **Android boots:** verify build identity, HOME launcher, touchscreen/display, Settings/input, Wi-Fi reconnect, Kodi discovery/manual connection, audio/subtitle selection, USB/ADB, charging/battery reporting, and reboot before considering the experiment successful.
4. **USB disconnects or the result is ambiguous:** treat status as unknown; do not repeat the write. Observe USB mode and use only the separately reviewed recovery route.

## Authorization boundary

The system write was explicitly approved by the owner for the exact image path, SHA-256, and `system` partition. Fastboot reported both image transfer and partition write as `OKAY`. No other partition write was authorized or performed.

## Bootloader unlock record — 2026-10-15

The separate bootloader unlock was explicitly authorized and completed.
Fastboot returned `OKAY` for one `oem unlock` command, then `fastboot reboot`
returned `OKAY`. ADB reconnected, and the owner confirmed Service Menu
`Bootloader unlocked: Yes`. The owner later separately approved the exact `system` partition operation documented above.

## Post-unlock physical read-only preflight — 2026-10-15

The E2003 was rechecked over ADB for the exact model and stock build before a
normal `adb reboot bootloader`. Fastboot identified one E2003 target, the
expected S1 bootloader, and `system` size `0x7d000000`; `getvar unlocked`
remained blank. After the operator confirmed the exact Sony Service Menu
status, the updated helper reported `READ-ONLY PREFLIGHT PASSED`. The helper
verified the local raw ext4 image's exact expected size, SHA-256 and file type.
It issued no write or reboot command. The host then ran `fastboot reboot`, and
ADB reconnected to E2003 / Android 4.4.4 / `25.0.A.2.31`. No partition was
read or written. This validates preflight plumbing and identity/capacity only;
it does not validate the bootloader's acceptance of `fastboot flash system`,
image write integrity, or Android boot.


## Flash and startup observation — 2026-10-15

Immediately before the write, the helper revalidated image size/hash/type,
Fastboot target count, product E2003, system capacity `0x7d000000`, and S1
bootloader identifier. Fastboot returned `Sending 'system' (2048000 KB) OKAY`
after 319.875 seconds and `Writing 'system' OKAY`; command total was 319.890
seconds. No other flash command was run. `fastboot reboot` returned `OKAY`.

After reboot the handset enumerated as Sony USB product `0fce:e1cb`, whose
interface is USB Mass Storage. It did not appear in `adb devices` or
`fastboot devices` during the observation window (about 45 seconds). Android
4.4 supports USB Mass Storage mode, so this USB identity alone does not prove
a boot failure. The phone's screen was not observable from the host; whether
Android reached its UI is **UNKNOWN**. No recovery or additional write attempt
was made. See Sony's [USB connection-mode support article](https://www.sony.com/electronics/support/articles/SX187901).
