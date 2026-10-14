#!/usr/bin/env bash
# Offline-only wrapper around the AOSP host-side unpack_bootimg.py.
# Copies the source image, leaving the original unchanged; never accesses a device.
set -euo pipefail

usage() { echo "Usage: $0 boot-or-recovery.img /path/to/unpack_bootimg.py new-output-directory" >&2; exit 2; }
[[ $# -eq 3 ]] || usage
image=$1
unpacker=$2
out=$3
[[ -f "$image" && -r "$image" ]] || { echo 'ERROR: input image must be a readable regular file' >&2; exit 1; }
[[ -f "$unpacker" && -r "$unpacker" ]] || { echo 'ERROR: unpack_bootimg.py must be a readable local file' >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo 'ERROR: python3 is required' >&2; exit 1; }
[[ ! -e "$out" ]] || { echo 'ERROR: output path already exists; choose a new directory' >&2; exit 1; }

parent=$(dirname -- "$out")
mkdir -p -- "$parent"
stage=$(mktemp -d "${TMPDIR:-/tmp}/farfar-boot-inspect.XXXXXXXX")
cleanup() { rm -rf -- "$stage"; }
trap cleanup EXIT
mkdir -- "$out"
cp -- "$image" "$stage/input.img"

printf 'Input SHA-256: '; sha256sum -- "$image"
printf 'Parser SHA-256: '; sha256sum -- "$unpacker"
printf 'Output directory: %s\n' "$out"
python3 "$unpacker" --boot_img "$stage/input.img" --out "$out"
echo 'Offline extraction completed. Review extracted files and parser output; no image was patched or repacked.'
