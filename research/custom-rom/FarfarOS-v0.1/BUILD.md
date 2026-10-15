# Build FarfarOS Experimental v0.1

## Host requirements

Linux Mint or a compatible Linux host, Python 3, `debugfs`, `e2fsck`, `file`, `keytool`, `jarsigner`, `sha256sum`, Android SDK `aapt2`, and at least 5 GB free space on the temporary/output filesystem. Keep all proprietary inputs and outputs out of Git.

The current build uses the pinned R10A `system.ext4` only as a filesystem container, then applies captured R7A file contents and metadata. The builder checks the R10A input SHA-256 and the installed OS APK signer. It also validates the owner-supplied animation archive, writes the two payloads, reads them back, and runs `e2fsck -fn`.

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
  /private/output/FarfarOS-E2003-R7A-v0.1-system.ext4
```

The output is a raw ext4 `/system` partition image plus an adjacent SHA-256 file. **It is not directly flashable.** Do not put it in GitHub Releases.

## Reproducibility and provenance

The image is reproducible only when the exact private R7A file tree and metadata capture, the pinned R10A ext4/tree pair, APK, and animation are available. Their hashes are written to the build log; the system image hash is emitted and recorded in the private sidecar. Do not commit the proprietary inputs, live device dumps, or generated partition image.

The root build script invokes `research/custom-rom/tools/create_r7a_system_image_poc.py`; the optional final argument enables boot-animation integration. Omitting it retains the earlier APK-only system POC behavior.
