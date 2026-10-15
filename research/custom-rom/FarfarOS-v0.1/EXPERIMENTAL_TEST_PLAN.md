# Experimental test plan

## Offline gates (completed before the authorized system write)

1. Confirm source image, APK signer/package/min API and animation hashes.
2. Build a new output image only; retain its SHA-256 and full build log.
3. Run `e2fsck -fn`, verify APK/animation by debugfs readback, and inspect owner/mode/SELinux metadata.
4. Independently inspect filesystem size, free blocks, `/build.prop`, launcher intent and boot-animation path.
5. Audit the exact boot ramdisk/init scripts for every mount, automatic format action and Sony bootstrap side effect. The existing R10A ramdisk marks `protect1`/`protect2` `autoformat`, invokes `wipedata`/`mr`, and starts `updatemiscta` (whose matching system binary references TA-write APIs). It is excluded from another boot attempt until runtime guards are understood and an acceptable ramdisk candidate is reviewed. A local variant that removes these actions exists for offline analysis only; omitting Sony bootstrap work may prevent startup, so that variant is also not ready for device testing.
6. Prepare the exact operation proposal with partition, image hash, backup state and failure modes. The owner separately authorized the exact `/system` write after the preflight passed.

The operation and outcome are recorded in [`SYSTEM_PARTITION_TRIAL_PROPOSAL.md`](SYSTEM_PARTITION_TRIAL_PROPOSAL.md). Fastboot preflight confirmed E2003, `system` type `ext4`, and exact 2,097,152,000-byte capacity. Because `getvar unlocked` is blank, the operator supplied the exact Service Menu confirmation interactively. The write returned `OKAY`. No raw system backup or validated R7A restore route exists.

## First startup observation (historical; superseded)

After the write, the phone enumerated as Sony USB Mass Storage (`0fce:e1cb`) and did not appear in ADB/Fastboot during the observation window. Android 4.4 supports this USB mode, so the USB identity alone does not establish failure. The screen was not observable from the host. On-device verification is still required: confirm whether Android/FarfarRemote UI appears; if it does, check build identity, touch/display, HOME selection, Settings/input, Wi-Fi, Kodi discovery/manual connection, remote navigation, Audio/Subtitles, timeout, USB/ADB, charging and battery status. Do not issue another write or recovery command based solely on the USB mode. touch/display, HOME selection, Settings and input, Wi-Fi association/reconnection, Kodi discovery/manual connection, navigation, Audio/Subtitles, screen timeout, USB/ADB, charging state, temperature and idle suspend/resume. Test reboot and power interruption only after basic boot is stable.

### Earlier temporary-boot attempt — 2026-10-15

An owner-authorized `fastboot boot` attempt used the local boot-container POC (SHA-256 `1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`). Fastboot acknowledged transfer, then reported a USB status-read failure as the phone re-enumerated with a mass-storage-only USB function. No ADB/Fastboot return was observed during the test window, so boot result is **INCONCLUSIVE**. No flash/erase/unlock/wipe command was used. This did not test the custom `/system` image; the installed system partition remained untouched.

## Stop criteria

Stop further changes if boot loops, ADB is unavailable beyond the agreed observation window, display/touch fails, Wi-Fi cannot recover, charging/battery reporting is abnormal, or the image writes outside the exact approved partition. Do not try unrelated partitions or generic images as recovery attempts.

## Owner-confirmed first boot and Kodi smoke test — 2026-10-15

The owner reported seeing FarfarOS, then Android's lock screen, selecting
FarfarRemote as Home, and observing FarfarRemote start. ADB subsequently
identified E2003 / Android 4.4.4 / firmware `25.0.A.2.31` and FarfarRemote
`0.4.7`. The owner confirmed Wi-Fi, Kodi connectivity and control. The owner
then confirmed Audio/Subtitles, portrait/landscape rotation, Settings,
Find My Kodi, and Wi-Fi reconnection after reboot. These are user-performed
physical-device tests, not host-automated tests.

In a subsequent full power-off/power-on test, the owner confirmed Android
skipped the lock screen and FarfarRemote automatically reconnected to Kodi.
This verifies the intended unattended startup path once on the target device.

Remaining checks: exhaustive remote-button coverage, off-USB charging,
sleep/wake behavior, extended stability, repeated cold boots and detailed
boot-animation timing. The earlier USB Mass Storage-only observation was
transient and is superseded by the successful startup. Do not infer broad
compatibility beyond the tested E2003 setup.
