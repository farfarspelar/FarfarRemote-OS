# E2003 bootloader unlock proposal — review only

**Status: NOT AUTHORIZED / NOT EXECUTED**

This proposal is for the exact connected Sony Xperia E4g E2003, Android 4.4.4,
firmware `25.0.A.2.31`, CDA `1293-7358 R7A`, using its S1 Fastboot interface.
It does not authorize a ROM/system write.

## Current evidence

- The Android Service Menu showed `Bootloader unlock allowed: Yes` but did
  **not** show `Bootloader unlocked: Yes`.
- Fastboot identified product `E2003` and bootloader
  `1290-9780 S1_Boot_MT6732_TC9PRA_9`; `getvar unlocked` returned no value.
- Fastboot connectivity works, but that does not mean the bootloader is
  currently unlocked.
- The experimental system image exists locally, but it has not been accepted
  or booted by this handset. A validated exact-R7A restoration path is still
  missing.

## What the unlock operation would do

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

## Proposed scope, if separately authorized

1. Reconfirm that exactly one Fastboot device is connected and reports product
   `E2003` and the expected S1 bootloader. Do not disclose its USB serial.
2. Use only an unlock code obtained by the owner directly from Sony's official
   unlock-code flow. Do not place the code or IMEI in Git, logs, shell history,
   or chat.
3. Issue only Sony's documented bootloader-unlock operation. Do not flash,
   erase, format, root, or write any other partition in the same session.
4. Wait for the handset to complete its factory reset and boot Android.
5. Recheck the Service Menu and accept success only if it explicitly shows
   `Bootloader unlocked: Yes`; record the new Android build/CDA without
   collecting personal identifiers.
6. Stop. A future system-image write would require a separate proposal and
   separate authorization. The missing restore path remains a distinct risk.

The exact command template from Sony's instructions is:

```sh
fastboot oem unlock 0x<OWNER-SUPPLIED-UNLOCK-CODE>
```

This template is documentation only. No code has been requested, received,
stored, or executed. No unlock or partition-write command has been sent.

## Decision required before execution

The owner must explicitly authorize this one operation after accepting the
factory reset and irreversible DRM-key consequence. Approval to develop or
build FarfarOS does not execute this proposal. Even after successful unlock,
the phone is not ready for a system-image flash because no exact restoration
route has been validated.
