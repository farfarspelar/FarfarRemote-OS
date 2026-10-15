# FarfarOS boot animation proof of concept

**Status: PARTIAL / OFFLINE ONLY.** This note records static validation and the
boundary of the attempted local image test. It does not authorize or describe a
flashable image.

## Input and static validation

The owner supplied `/mnt/data/Downloads/FarfarOS_bootanimation_bundle.zip`.
Its `COPY_PASTE_TO_CODEX.md` specifies the E2003 target, Android-ready archive,
540×960 frames, 18 fps, a one-play intro (`part0`) and a looping `part1`.
The bundle's nested `bootanimation.zip` SHA-256 is
`543682f34508e7031c5da63898285f86cf72bbcd98b572c859204f4502131eef`, matching
`graphics/bootanimation/bootanimation.zip` byte for byte.

Previously completed archive checks found 15 entries, no enclosing directory,
`desc.txt` at the root, and ZIP `STORED` entries. CRC validation passed; all 14
frames are 540×960 RGB PNGs. The Sony E2003 `bootanimation` executable contains
the expected `/data/local/bootanimation.zip` and
`/system/media/bootanimation.zip` path strings, as well as Sony-specific
fallback paths. This is static evidence only; Sony's exact runtime selection
order and playback have not been observed on-device.

## Local image-copy attempt

The available ext4 preinstall POC is an R10A candidate, while the physical
phone is R7A (`1293-7358`). It is not an exact firmware base. A separate copy
was created outside Git at:

`/mnt/data/FarfarRemote-E2003-R10A-system-bootanimation-POC.img`

The completed copy had the same SHA-256 as its source image,
`35d8a29e1ac8b91e04c2975a832ef686166fc2d21b775669861234772fb8b731`.
Subsequent read-only `debugfs` inspection of the copy stalled in host storage
I/O. A termination signal was sent to the blocked inspection process; it was
still in uninterruptible I/O wait at the time this note was written. No
`debugfs -w` command ran, and no image modification was attempted. The source
image was not modified. The copy is not a boot-animation POC and should be
deleted after no process has it open; it must never be flashed.

## Device test status and safe next step

On the physical E2003, `/data/local` is root-owned and not writable to the
authorized ADB shell (`ro.secure=1`, `ro.debuggable=0`). Replacing
`/system/media/bootanimation.zip` requires privileged system access. Therefore
the bundle was not installed, no reboot was performed for this test, and
playback remains unverified. Do not work around this by remounting `/system` or
trying unrelated root tools.

To continue the image experiment, first resolve the host storage latency and
use an exact, verified R7A base or a newly reproducible R7A image. Operate on a
new copy; replace only `/system/media/bootanimation.zip`; set owner `root:root`,
mode `0644`, and SELinux label `u:object_r:system_file:s0`; read the file back
and compare its SHA-256; then run a read-only filesystem check. The resulting
ext4 image would still be an offline, non-flashable artifact until Sony
packaging, boot-chain compatibility, and rollback are independently verified.

## Recovery and status

No phone partitions, system files, or boot settings were changed. The stock
animation remains in use. The lowest-risk device playback route is still a
temporary `/data/local/bootanimation.zip` override followed by removal of only
that override, but current ADB permissions do not allow it. Any future attempt
requires a verified, separately approved elevated route and a known recovery
path.
