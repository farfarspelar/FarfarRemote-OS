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

## Local image POC

The available ext4 preinstall POC is an R10A candidate, while the physical
phone is R7A (`1293-7358`). It is not an exact firmware base. A separate local
copy was created outside Git at:

`/tmp/farfar-e2003-system-bootanimation-poc.img`

Source image SHA-256: `931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949`.
Modified POC SHA-256: `06a9156bcbbbbffb60b3c8d7dcf44785e1b66def2b5ffe574709278388ebb6ef`.
The source image hash remained unchanged.

The POC replaces only `/system/media/bootanimation.zip`. The resulting inode
was verified as a regular file, owner `root:root`, mode `0644`, and SELinux
label `u:object_r:system_file:s0`. A readback from the image matched the
committed asset SHA-256 exactly; `unzip -t` passed; and `e2fsck -fn` exited 0.
This validates archive integration and ext4 metadata on the host. It is still
only an R10A offline system partition—not an R7A image, complete ROM, Sony
firmware package, boot-tested image, or flashable artifact.

An earlier duplicate copy on `/mnt/data` triggered slow host-storage I/O during
read-only inspection. That inspection received a termination signal and
eventually exited; it did not write to the image. The duplicate is disposable
and separate from the verified `/tmp` POC. The worktree input and phone were
not modified.

## Device test status and safe next step

On the physical E2003, `/data/local` is root-owned and not writable to the
authorized ADB shell (`ro.secure=1`, `ro.debuggable=0`). Replacing
`/system/media/bootanimation.zip` requires privileged system access. Therefore
the bundle was not installed, no reboot was performed for this test, and
playback remains unverified. Do not work around this by remounting `/system` or
trying unrelated root tools.

To continue, repeat this proven edit against an exact, verified R7A base or a
newly reproducible R7A system image, while keeping it separate from the source.
Even then, the ext4 image remains an offline artifact until Sony packaging,
boot-chain compatibility, and rollback are independently verified.

## Recovery and status

No phone partitions, system files, or boot settings were changed. The stock
animation remains in use. The lowest-risk device playback route is still a
temporary `/data/local/bootanimation.zip` override followed by removal of only
that override, but current ADB permissions do not allow it. Any future attempt
requires a verified, separately approved elevated route and a known recovery
path.
