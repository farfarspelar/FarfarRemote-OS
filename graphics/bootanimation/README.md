# FarfarOS boot animation

This directory contains the owner-provided FarfarOS Android boot animation and its editable source frames.

## Files

- `bootanimation.zip` is the Android-ready archive (SHA-256: `543682f34508e7031c5da63898285f86cf72bbcd98b572c859204f4502131eef`).
- `source/desc.txt` and `source/part0`, `source/part1` are the source assets extracted from the accompanying bundle.
- The bundle's `COPY_PASTE_TO_CODEX.md` requested integration into the OS research/assets track, verification of the E2003 lookup path, and a reversible test where possible.

## Static format checks

The archive has 15 entries, no enclosing top-level folder, and only ZIP `STORED` entries (no compression). The root contains `desc.txt`; the remaining 14 PNGs are in `part0/` and `part1/`. `unzip -t`/Python CRC validation passed. All frames are 540×960 RGB PNGs with no alpha channel, so every frame is fully opaque. `desc.txt` is:

```text
540 960 18
p 1 0 part0
p 0 0 part1
```

This means an 18-fps single-play intro followed by a loop while Android's boot animation service remains active. The E2003 has a 540×960 display. These checks validate archive structure and dimensions, not playback on the handset.

## E2003 lookup and installation status

Read-only inspection of the connected E2003 found:

- `/system/bin/bootanimation` is present and contains references to `/data/local/bootanimation.zip` and `/system/media/bootanimation.zip`; it also contains Sony-specific fallback paths `/system/media/bootanimation-encrypted.zip` and `/data/customization/extra-bootanimation.zip`.
- The stock `/system/media/bootanimation.zip` exists. The encrypted and customization override files queried were absent.
- `/data/local` is `root:root` mode `0751`; the authorized ADB shell is not allowed to write there (`test -w /data/local` failed). The build reports `ro.secure=1` and `ro.debuggable=0`; there is no verified root path in this work.
- The asset was **not installed on the phone**, Android system files were not changed, and no reboot was performed for animation testing. Replacing `/system/media/bootanimation.zip` would require elevated write access and a system change, so that path is not used in this step.
- An offline image-copy test was started from an R10A system-image POC, but host storage I/O stalled while multiple image-edit commands were pending. Those commands were stopped, the incomplete derived image was removed, and the input R10A POC was left untouched. No modified system image was produced.

Android's AOSP KitKat boot-animation implementation documents `/data/local/bootanimation.zip` as a user override before the system copy ([AOSP bootanimation source](https://android.googlesource.com/platform/frameworks/base/+/android-4.4.4_r2/cmds/bootanimation/BootAnimation.cpp)). The Sony binary's embedded path strings corroborate that these paths are present in this firmware. The exact selection order of Sony's customized implementation has not been dynamically tested.

## Safe next test

The least invasive device test is to copy this file to `/data/local/bootanimation.zip`, verify it is readable as `0644`, reboot once, and then remove only that override to restore the stock selection. The current ADB shell cannot write to `/data/local`, so this test is blocked unless a separately approved, verified root/test-image route is available. Do not remount or modify `/system` as a workaround. A local system-image POC is separate from an on-device playback test and must be clearly marked non-flashable until its exact base and packaging are validated.

## Provenance

The boot animation was supplied by the project owner in the `FarfarOS_bootanimation_bundle.zip` bundle. The visual design is project-directed FarfarOS artwork. The individual frame creation history and any third-party material used within those frames were not included in the bundle; do not claim a more specific generation or third-party-license status without that provenance.
