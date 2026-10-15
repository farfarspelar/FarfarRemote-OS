# FarfarOS v0.1 `/system` trial — write and first boot completed

## Outcome update — 2026-10-15

The initial post-write USB observation documented below was inconclusive at
the time. It has since been superseded: the owner powered the phone on,
observed FarfarOS and Android's lock screen, selected FarfarRemote as Home,
and confirmed the app launched, connected to Wi-Fi and controlled Kodi. ADB
also reconnected and identified the expected E2003 / Android 4.4.4 / firmware
combination. The exact `/system` image therefore passed a first boot and
network/Kodi smoke test on the target. The owner subsequently also confirmed
Audio/Subtitles, rotation, Settings, Find My Kodi and Wi-Fi reconnection after
reboot. These are owner-reported device tests. Some exhaustive, long-duration
checks and a validated restore route remain outstanding.

The owner then performed a full power cycle and confirmed startup skipped the
lock screen and FarfarRemote automatically reconnected to Kodi.

## Scope

The owner approved the exact image, SHA-256 and `system` target after a read-only preflight. Fastboot reported the image transfer and `system` write as `OKAY`. The operation targeted only the E2003 `system` partition; `boot`, `fotakernel`, bootloader, `seccfg`, TA, NVRAM, calibration and userdata were not included. The current stock kernel and ramdisk remain in place. Subsequent first-boot and feature-test results are recorded in the outcome update above; this remains an experimental system-only build, not a complete ROM package.

## Candidate

- Device target: Sony Xperia E4g E2003, Android 4.4.4 / API 19, build
  `25.0.A.2.31`, CDA `1293-7358 R7A`.
- Partition: Fastboot label `system`; read-only Fastboot reports type `ext4`
  and size `0x7d000000` = **2,097,152,000 bytes**.
- Image: private artifact
  `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4`.
- Image size: **2,097,152,000 bytes**, an exact byte-size match to the
  reported partition.
- SHA-256:
  `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`.
- Format check: identified as ext4; `e2fsck -fn` completed all five passes.
- Content check: compared to the private live R7A `/system` capture; all 4,447
  original paths matched type, mode, UID, GID, SELinux label, and symlink
  target. All original regular-file contents matched except the intentionally
  replaced boot animation. FarfarRemote OS APK and boot animation readbacks
  were separately verified. See `BUILD_REPORT.md` for the full audit.

The image is a reconstructed ext4 filesystem, not a raw readback of the
partition and not a Sony-signed FTF/SIN package. The filesystem container was
based on an E2003 R10A image, then populated with the captured R7A tree and
metadata. Exact size and file-level comparison are encouraging but do not
prove S1 Fastboot accepts it or that Android will boot it.

## Read-only bootloader status checks — 2026-10-15

The device was rebooted from Android into Fastboot and returned to Android
using ordinary reboot commands only. Read-only results:

| Query | Result |
|---|---|
| `product` | `E2003` |
| `unlocked` | empty response |
| `secure` | `yes` |
| `partition-size:system` | `0x7d000000` |
| `partition-type:system` | `ext4` |

ADB reconnected and confirmed E2003 / Android 4.4.4 / API 19 /
`25.0.A.2.31` / CDA `1293-7358 R7A`. No partition command was sent. Fastboot
did not expose a usable `unlocked` value. `secure: yes` does not establish
whether this bootloader is locked.

The pre-unlock Service Menu showed `Bootloader unlock allowed: Yes`, not
`Bootloader unlocked: Yes`. After the separately authorized Sony unlock, the
owner confirmed the Service Menu now says `Bootloader unlocked: Yes`. ADB has
reconnected and confirms E2003 / Android 4.4.4 / API 19 / build
`25.0.A.2.31` / CDA `1293-7358 R7A`. This is owner-confirmed unlock status;
ordinary ADB remains UID 2000 and Android root is not present.

The [Xperia bootloader checklist](https://docs.sailfishos.org/Support/Help_Articles/Managing_Sailfish_OS/Checklist_for_Sailfish_OS/#xperia-bootloader)
describes `Bootloader unlock allowed: Yes` as the state where unlocking is
still the next step. The owner later separately authorized and completed the unlock; the
status is recorded below.

Sony's [official unlock guide](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader)
says the unlock triggers a factory reset and that the DRM security keys cannot
be restored afterward; it also says unlocking alone does not grant root. The
owner has said user data need not be preserved, but the irreversible DRM-key
loss and possible device-specific feature effects remain a separate
consequence. The guide does not establish which E2003 functions depend on those
keys.

## Backup and recovery status

- **No raw `/system` backup exists.** A stock-tree reconstruction exists, but
  it is not a byte-for-byte raw partition backup and is not validated as a
  restore image.
- No exact, traceable E2003 R7A FTF/SIN restore package has been verified.
- Sony Xperia Companion repair is offered for Windows/macOS generally, but
  E2003/R7A eligibility and the firmware/CDA it would offer are unknown. Linux
  Mint is the available host; no working Linux repair route is established.
- A historical E2003 recovery candidate is R5A and has not been boot-tested on
  this R7A device.
- Existing `boot` and `fotakernel` would remain untouched by the proposed
  system-only write. This reduces scope but does not guarantee recovery if the
  new system fails to boot or the bootloader refuses the image.

**Restore status: NO VALIDATED RESTORE IMAGE OR PROCEDURE.** The owner has
explicitly asked to proceed despite this gap and has accepted soft-brick risk.
This is a material consequence, not a recovery capability: a rejected or
partially written image, boot loop, or non-booting Android could require a
repair path that is unavailable from the current Linux Mint setup.

## Potential operation, for review only

The owner has confirmed `Bootloader unlocked: Yes`. Fastboot subsequently
accepted the `system` alias and reported the raw ext4 transfer/write as
`OKAY`. The actual on-device filesystem contents and Android boot remain
unverified. A read-only preflight is available at
`research/custom-rom/tools/preflight_e2003_system_write.sh`; because this
bootloader returns an empty `getvar unlocked`, it now fails closed unless the
operator interactively confirms the exact Service Menu status. This helper
never writes or reboots. The approved image was written to `system`; no other partition was written. Do not
substitute a boot, recovery, FOTA, sparse image, or other partition. An
interrupted write or rejected format may leave Android unable to start.

## Decision

The image is ready for review as a narrowly scoped experimental system-only
trial, not as a verified flashable ROM. The owner has confirmed the unlocked
state and has accepted proceeding without a proven restore base. The exact write was separately authorized and reported `OKAY`. First boot
was not confirmed: after `fastboot reboot`, USB exposed a Sony Mass Storage
interface (`0fce:e1cb`) and neither ADB nor Fastboot became available during
approximately 45 seconds. Screen state is unknown. No recovery attempt or
additional write was made. A successful write does not establish a successful
Android boot.

### Bootloader unlock status addendum — 2026-10-15 (superseded by confirmation below)

The owner explicitly authorized the separate unlock operation. The guarded
helper revalidated E2003 / `25.0.A.2.31` / `1293-7358 R7A` and one Fastboot
target; Fastboot returned `OKAY` for the Sony unlock command and reboot. The
system-image write described above had not yet been executed at that historical checkpoint; the later write is recorded above.

### Post-unlock artifact verification — 2026-10-15

The owner confirmed Service Menu `Bootloader unlocked: Yes`. ADB identifies
E2003 / Android 4.4.4 / API 19 / firmware `25.0.A.2.31`; shell UID is 2000.
The raw system image remains 2,097,152,000 bytes, SHA-256
`cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`;
`e2fsck -fn` passed all five passes. The Android sparse image round-tripped
byte-for-byte to raw ext4. Embedded FarfarRemote is `org.farfarremote`
version `0.4.7`, min SDK 19, target SDK 28, signed by the Android Debug
certificate (SHA-256 `63f9336d0038b8ebe9ac8224f8869e1f871828d81b6269372315ce055cf607fd`).
The `system` partition was written under the owner’s separate approval; no other partition was written.

### First startup observation — 2026-10-15

Fastboot reported transfer and write success for the reviewed `system` image.
After normal reboot, USB enumerated as `0fce:e1cb` with a Mass Storage
interface. ADB and Fastboot remained unavailable during the observation
window. Android 4.4 supports USB Mass Storage mode, so this USB identity alone
does not establish whether Android boot completed. The screen was not
observable; startup is **inconclusive and not verified**. No additional device
commands that write data were issued. Sony documents MSC selection for Android
4.2–5.1 in its [USB connection-mode support article](https://www.sony.com/electronics/support/articles/SX187901).
