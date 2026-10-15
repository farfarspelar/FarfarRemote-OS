# Build FarfarOS Experimental v0.1

## Host requirements

Linux Mint or a compatible Linux host, Python 3, `debugfs`, `e2fsck`, `file`, `keytool`, `jarsigner`, `sha256sum`, Android SDK `aapt2`, and at least 5 GB free space on the data filesystem. Keep all proprietary inputs and outputs out of Git.

## Disk layout

Large local research inputs migrated from `/tmp` are preserved at:

`/mnt/data/FarfarRemote-Research-POC/workspaces/tmp-migration-2026-10-15/`

The original `/tmp/<name>` paths are symlinks to those retained files, so existing local references continue to work. Do not remove the symlink targets while a build or investigation is using them. The Gradle cache is also stored on the data filesystem at `/mnt/data/FarfarRemote-Research-POC/build-cache/gradle` and linked from `~/.gradle`.

The build wrapper defaults to:

- Output: `/mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/`
- Temporary files: `/mnt/data/FarfarRemote-Research-POC/tmp/`

It verifies that the data root is on a filesystem separate from `/` and has at least 5 GiB free before creating build directories. It also verifies that the temporary directory is on that same data filesystem, exports `TMPDIR`, `TEMP` and `TMP`, and refuses output outside the data-backed build directory or inside the Git repository. This prevents a missing `/mnt/data` mount from silently filling `/`. To use another data volume, set `FARFAR_DATA_ROOT` and optionally `FARFAR_TMPDIR` before invoking it. The Python builder stages its ext4 image alongside the requested output, so keep the output on the data filesystem as well.

The current build uses the pinned R10A `system.ext4` only as a filesystem container, then applies captured R7A file contents and metadata. The builder checks the R10A input SHA-256 and the installed OS APK signer. It also validates the owner-supplied animation archive, writes the two payloads, reads them back, and runs `e2fsck -fn`.

The builder pins e2fsprogs timestamps for repeatable output. By default it uses `SOURCE_DATE_EPOCH=1704067200` (2024-01-01 UTC); set `SOURCE_DATE_EPOCH` to another non-negative Unix timestamp to select a different build epoch. The value is passed to `debugfs` as `E2FSPROGS_FAKE_TIME` and to `e2fsck` as `E2FSCK_TIME` as well, because e2fsck 1.47.0 uses its own clock for superblock timestamps.

## Required local inputs

Obtain these only from the already reviewed local research workspace / owner device; do not substitute another Xperia build:

1. E2003 `25.0.A.2.31` R10A `system.ext4` candidate (SHA-256 pinned in the builder).
2. Extracted R10A system tree corresponding to that image.
3. Read-only E2003 R7A `/system` file tree.
4. Private metadata capture from the same E2003 R7A `/system`.
5. FarfarRemote OS APK with package `org.farfarremote`, min API 19, and the existing E2003 signing certificate.
6. Project `graphics/bootanimation/bootanimation.zip`.

The build tool refuses output inside the Git repository and refuses to overwrite an existing image.

## Command

```bash
export AAPT2_BIN="$HOME/Android/Sdk/build-tools/35.0.0/aapt2" # change to the installed path
research/custom-rom/FarfarOS-v0.1/tools/build_farfaros_v0.1_system.sh \
  /private/path/farfar-e2003-system-R10A.img \
  /private/path/farfar-e2003-r10a-system-tree \
  /private/path/farfar-e2003-r7a-system-full/system \
  /private/path/farfar-e2003-r7a-metadata-verified.txt \
  dist/FarfarRemote-OS-Android4.4plus-API19plus-v0.4.7.apk \
  graphics/bootanimation/bootanimation.zip \
  /mnt/data/FarfarRemote-Research-POC/builds/FarfarOS-v0.1/FarfarOS-E2003-R7A-v0.1-system.ext4
```

The output is a raw ext4 `/system` partition image plus an adjacent SHA-256 file. **It is not directly flashable.** Do not put it in GitHub Releases.

For offline packaging research only, `tools/ext4_to_android_sparse.py <raw.ext4> <new.sparse.img>` creates a standard Android sparse v1 container. It refuses to overwrite an existing destination and leaves the raw image unchanged. The current sparse output round-tripped byte-for-byte through the preserved MediaTek `simg2img` utility, but neither sparse nor raw format acceptance by this handset's bootloader has been established. This does not convert the image into a Sony-signed SIN or make it flashable; see `BUILD_REPORT.md`.

## Rebuild repeatability and provenance

The build can be repeated only when the exact private R7A file tree and metadata capture, the pinned R10A ext4/tree pair, APK, and animation are available. Their hashes are written to the build log; the system image hash is emitted and recorded in the private sidecar. After timestamp pinning, two full builds from the same local inputs on 2026-10-15 produced byte-identical 2,097,152,000-byte output with SHA-256 `cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d`. Both runs passed payload readback validation and `e2fsck -fn`. This demonstrates reproducibility for this host/toolchain/input set; repeat on the intended build host before treating it as portable. Do not commit the proprietary inputs, live device dumps, or generated partition image.

The root build script invokes `research/custom-rom/tools/create_r7a_system_image_poc.py`; the optional final argument enables boot-animation integration. Omitting it retains the earlier APK-only system POC behavior.
