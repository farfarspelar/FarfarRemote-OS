# E2003 bootloader unlock operation record

**Status: UNLOCK COMMAND ACCEPTED; POST-RESET VERIFICATION PENDING**

This proposal is for the exact connected Sony Xperia E4g E2003, Android 4.4.4,
firmware `25.0.A.2.31`, CDA `1293-7358 R7A`, using its S1 Fastboot interface.
It does not authorize a ROM/system write.

## Current evidence

- The Android Service Menu showed `Bootloader unlock allowed: Yes` but did
  **not** show `Bootloader unlocked: Yes`.
- Fastboot identified product `E2003` and bootloader
  `1290-9780 S1_Boot_MT6732_TC9PRA_9`; `getvar unlocked` returned no value.
- Fastboot connectivity works, but that does not mean the bootloader is
  currently unlocked until the post-operation status is checked.
- The experimental system image exists locally, but it has not been accepted
  or booted by this handset. A validated exact-R7A restoration path is still
  missing.

## Fresh preflight after owner authorization — 2026-10-15

The owner explicitly authorized the E2003 bootloader unlock, factory reset,
and irreversible DRM-key loss. The connected Android device was rechecked
read-only and reported model/device `E2003`, fingerprint
`Sony/E2003/E2003:4.4.4/25.0.A.2.31/4Pf_Nw:user/release-keys`, CDA `1293-7358`
revision `R7A`, Android 4.4.4/API 19. ADB rebooted it to Fastboot; exactly one
nonempty Fastboot target was present and read-only queries again reported
product `E2003`, bootloader `1290-9780 S1_Boot_MT6732_TC9PRA_9`, blank
`unlocked`, and `secure: yes`. It was returned to Android, and ADB reconfirmed
the same identity. The masked code was entered into the guarded helper and was
not saved in the repository or printed by the helper. Fastboot returned
`OKAY` for the single `oem unlock` command (3.809 seconds). No system/boot image
or other partition image was flashed.

Afterward `fastboot reboot` returned `OKAY`. The handset enumerated on USB as
an Android device, but ADB reported zero authorized targets; this is consistent
with the factory reset disabling USB debugging or requiring host reapproval,
but the exact screen state is **UNKNOWN**. The Service Menu has not yet been
rechecked, so record the result as **unlock command accepted; actual unlocked
status pending post-reset verification**. No additional device command has
been sent since reboot.

## Operation effects

Sony's official procedure requires an unlock code and uses the device's
Fastboot connection. Sony states unlocking triggers a factory reset that
erases user data and settings. Sony also says unlocking alone does not grant
root, that DRM security keys cannot be restored afterward, and that the device
cannot be returned to its locked/original state through that process. Sony
warns unsigned ROMs can lose functionality and may permanently damage the
device. The available evidence does not identify which E2003 functions depend
on its DRM keys.

Official references:

- [Sony Open Devices: unlock risks and preparation](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader)
- [Sony Open Devices: Fastboot unlock procedure](https://opendevices.sony.net/aosp-on-xperia-open-devices/get-started/unlock-bootloader/how-to-unlock-bootloader)

## Scope performed

1. Reconfirmed exact E2003 Android build/CDA and the S1 bootloader; exactly one
   Fastboot target was present. The USB serial was not included in the report.
2. The owner provided the code through hidden local terminal input. The code is
   not stored in Git or this report.
3. Issued Sony's documented unlock command once. Fastboot returned `OKAY`.
4. Issued `fastboot reboot`; it returned `OKAY`.
5. The handset enumerated as Android USB, but ADB did not reconnect. Service
   Menu verification of `Bootloader unlocked: Yes` remains pending.
6. No system/boot/recovery image was flashed. System-image testing remains a
   separate, unauthorized operation and has no validated restore path.

The command template used by the helper was:

```sh
fastboot oem unlock 0x<OWNER-SUPPLIED-UNLOCK-CODE>
```

The owner supplied the code locally through hidden terminal input. Do not copy
the code into this document, a log, or Git.

The repository helper
[`tools/unlock_e2003_bootloader.sh`](tools/unlock_e2003_bootloader.sh) is
the guarded helper used for the authorized operation. It reads the owner's
code without
echo, validates the exact Android and Fastboot identities, requires exactly
one Fastboot target, and asks for the full consequence-specific authorization
phrase. It enters Fastboot with ADB, performs read-only Fastboot identity
queries, and issues no partition-write command other than Sony's `oem unlock`.
It contains no key and does not flash any image. Fastboot requires the code as
a command-line argument, so it may be briefly visible to processes running as
the same local user while the unlock command is executing.

## Remaining verification and next operation

The unlock operation was explicitly authorized and Fastboot accepted it. To
verify the resulting state, complete Android's first-start setup if shown,
re-enable USB debugging, approve this host, and inspect Service info >
Configuration > Rooting Status for `Bootloader unlocked: Yes`. The current
system-image trial remains a separate operation: no exact restoration route
has been validated, and no flash authorization has been given.
