# E2003 R7A system restore reconstruction

**Status: OFFLINE FILE-TREE RECONSTRUCTION ONLY — NOT A RAW BACKUP OR TESTED RESTORE IMAGE**

## Result

An offline reconstruction was created from the reviewed FarfarOS v0.1 system
image by reversing its two intentional `/system` changes:

1. Remove `/system/app/FarfarRemote.apk`.
2. Restore the captured E2003 R7A `/system/media/bootanimation.zip`.

The restored animation matches the private R7A capture byte-for-byte
(`cf580ff5826d3c0aaff7d927dd8569906fdff9a96626f73fb1ed73c8dd605445`). The
FarfarRemote APK is absent from `/system/app`. `e2fsck -fn` completed cleanly.

Local output at the time of creation:

- `/tmp/FarfarOS-E2003-R7A-stock-tree-reconstruction-v0.1.ext4`
- Size: 2,097,152,000 bytes
- SHA-256: `9942db8cdc048ff7ba9522160c1bf8aba3dcb6e6ce5e1c910f444bbed53880dd`

The checksum sidecar is adjacent to the image. The artifact and source firmware
inputs are intentionally not committed.

## What this does and does not restore

This is a new ext4 image built from the previously captured R7A `/system`
file tree and metadata, using the inspected E2003 R10A ext4 image as a
container. It restores the captured file contents and normal ownership, mode,
and SELinux label for the stock boot animation. It is **not** a byte-for-byte
copy of the live system partition; filesystem UUID, allocation, inode
timestamps, and other ext4 metadata may differ. It is not Sony-signed firmware,
and the E2003 S1 bootloader has not been shown to accept it. No hardware restore
test has been performed.

The existing builder and this reconstruction script operate only on local
files. They do not issue ADB, Fastboot, MTKClient, or Flashtool commands.

## Rebuild

The private R7A capture is required. On a host with the data volume healthy
and mounted, run:

```sh
python3 research/custom-rom/tools/rebuild_e2003_r7a_stock_system_candidate.py \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system-post-storage.ext4 \
  /mnt/data/FarfarRemote-Research-POC/workspaces/tmp-migration-2026-10-15/farfar-e2003-r7a-system-full/system/media/bootanimation.zip \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-stock-tree-reconstruction-v0.1.ext4
```

The script pins the source image and R7A animation hashes, refuses overwrite,
requires substantial free space on the data filesystem, removes only the
FarfarRemote system APK, restores the captured animation, verifies the
animation readback and APK absence, and runs a non-repairing ext4 check.

## Host storage incident during build

During an attempted run on `/mnt/data`, `debugfs` entered uninterruptible disk
sleep while updating its ext4 journal. The kernel also showed a `jbd2/mmcblk0p1`
thread already blocked for several days. The separately built `/tmp` artifact
above completed and validated on the host SSD. The incomplete output under
`/mnt/data/.../FarfarOS-E2003-R7A-stock-tree-reconstruction-v0.1.ext4` must not
be used unless its own checks finish and the hash is independently verified.
Resolve the data-volume I/O/journal issue before relying on it for future ROM
builds or storing the validated fallback there.

## Effect on live-write readiness

This improves the available file-level fallback for `/system`, but does not
make the proposed experiment ready for a device write. Remaining blockers are
listed in [`FLASH_EXPERIMENT_PROPOSAL.md`](FLASH_EXPERIMENT_PROPOSAL.md): exact
bootloader unlock state, acceptance of a raw ext4 payload by this E2003 S1
Fastboot, and any hardware boot result remain unverified. The reconstruction
is not a proven recovery method.
