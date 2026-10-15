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

Candidate command, **shown for review only and not run**:

```sh
fastboot -i 0x0fce flash system \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4
```

## Evidence and unknowns

- **VERIFIED, historical read-only observations:** handset product E2003; bootloader string `1290-9780 S1_Boot_MT6732_TC9PRA_9`; Android build `25.0.A.2.31`; customization R7A; system alias mapped to `mmcblk0p19`; reported system capacity `2,097,152,000` bytes.
- **REPORTED:** owner says the bootloader is unlocked.
- **UNKNOWN:** current unlock state. Prior `getvar unlocked` returned no value; `secure: yes` was reported. Current `fastboot devices` is empty.
- **UNKNOWN:** whether this S1 bootloader accepts the `system` Fastboot partition alias and raw ext4 payload. Flashtool's public source has a generic `fastboot flash system <image>` operation, but does not establish E2003 bootloader acceptance. See the pinned [Flashtool implementation](https://github.com/Androxyde/Flashtool/blob/7529dce9a1ffb81e365ba1d7e15f6773463ffd7a/Flashtool/src/main/java/org/flashtool/jna/adb/FastbootUtility.java).
- **UNKNOWN:** whether first boot will complete with the stock R7A boot/FOTA and this reconstructed system. No test of this system image has occurred on hardware.
- **INCONCLUSIVE prior observation:** a separate `fastboot boot` Android-container POC transferred, then USB disconnected with `Status read failed`; no boot result was observable. That experiment did not write the system partition and does not validate this image.

## Backup and recovery position

- A complete raw backup of the live R7A `system` partition is **not available**. A matching file tree/metadata capture exists, and the R10A container plus generated ext4 images are retained, but these are not byte-for-byte backups of the live partition.
- Exact R7A stock firmware restoration has **not** been verified.
- Sony S1 service/Flashmode transport was observed previously, but no exact R7A repair package or successful restore procedure was verified.
- A historical E2003 TWRP image passed static checks but was built/reported for R5A and has not been boot-tested on this R7A handset.
- Therefore recovery from a failed system-only experiment is **not guaranteed**. A soft brick/boot loop may require a service repair route that is currently unverified.

## Required read-only preflight before considering authorization

With the handset physically present and in Fastboot, record fresh output for:

```sh
fastboot devices
fastboot getvar product
fastboot getvar version-bootloader
fastboot getvar secure
fastboot getvar unlocked
fastboot getvar partition-size:system
```

Confirm `product` is exactly `E2003`, the system size is exactly `0x7d000000` bytes, and the handset identity/bootloader match the target above. A missing or inconsistent value is a stop condition; do not infer an alias or proceed based on the old capture. Re-check the image size and SHA-256 immediately before any separately approved write.

## Expected outcomes and failure modes

1. **Fastboot rejects the alias/image before writing:** no successful installation is established; capture output and stop. Do not try guessed aliases.
2. **Write reports success but Android fails to boot:** likely system/boot/framework mismatch or damaged filesystem; do not wipe userdata or write another partition as an improvised fix.
3. **Android boots:** verify build identity, HOME launcher, touchscreen/display, Settings/input, Wi-Fi reconnect, Kodi discovery/manual connection, audio/subtitle selection, USB/ADB, charging/battery reporting, and reboot before considering the experiment successful.
4. **USB disconnects or the result is ambiguous:** treat status as unknown; do not repeat the write. Observe USB mode and use only the separately reviewed recovery route.

## Authorization boundary

No write command has been issued under this proposal. Running the candidate `fastboot flash system` command requires a separate explicit approval naming this exact image, SHA-256, and the `system` partition after the read-only preflight is available. Broad approval to continue ROM research is not treated as approval for this particular partition write.
