# Proposed FarfarOS v0.1 `/system` trial — not authorized or executed

## Scope

This proposal evaluates a first trial that writes **only** the E2003 `system`
partition. It would leave the installed `boot`, `fotakernel`, bootloader,
`seccfg`, TA, NVRAM, calibration, and user-data partitions untouched. The
current stock kernel and ramdisk would therefore remain in place. This is a
proposal, not a flash instruction or authorization.

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

The Android Service Menu was then checked read-only at Service info >
Configuration > Rooting Status. It displayed `Bootloader unlock allowed: Yes`;
it did not display `Bootloader unlocked: Yes`. These are distinct states:
the former means unlocking is permitted, while the latter means it has already
been done. Current evidence therefore does **not** verify an unlocked
bootloader, despite the earlier owner report. Treat it as **not unlocked / not
verified** until the Service Menu explicitly reports `Bootloader unlocked:
Yes`. The UI hierarchy was inspected locally; temporary diagnostic output was
removed and FarfarRemote was restored to the foreground.

The [Xperia bootloader checklist](https://docs.sailfishos.org/Support/Help_Articles/Managing_Sailfish_OS/Checklist_for_Sailfish_OS/#xperia-bootloader)
describes `Bootloader unlock allowed: Yes` as the state where unlocking is
still the next step. No unlock command or unlock-code workflow was run.

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

**Recovery readiness: BLOCKED.** There is no validated way to restore the
original system partition if this image is rejected, partially written, or
fails during boot.

## Potential operation, for review only

The proposed system write is currently blocked even before considering the
missing recovery path: the bootloader's unlocked state is not verified. A
future system-only trial would require (1) a separately authorized and
successfully completed bootloader-unlock operation if the phone is still
locked, (2) independent confirmation that it now reports `Bootloader
unlocked: Yes`, and (3) separate explicit authorization for the exact system
image hash and partition write. No unlock or flash command has been run. Do
not substitute a boot, recovery, FOTA, sparse image, or other partition. A
transfer/write interruption may leave Android unable to start.

## Decision

The image is sufficiently validated for a **reviewable system-only trial
proposal**, but it is not ready to flash. Both the unlocked state and a
validated restoration route are missing. Bootloader unlocking is a separate,
potentially data-wiping operation and is not authorized by this proposal.
Even if those blockers are later resolved, the owner must separately
authorize writing this exact SHA-256 to the `system` partition and accept the
remaining risk. First-boot checks must use the stock boot chain and stop
immediately on unexpected partition activity or device behavior.
