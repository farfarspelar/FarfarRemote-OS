#!/usr/bin/env bash
set -euo pipefail

# Build an offline R7A-matched /system ext4 experiment. Does not run ADB,
# fastboot, MTKClient, flash tools, or write to a connected device.
if [[ $# -ne 7 ]]; then
  echo "Usage: $0 <R10A-system.ext4> <R10A-tree> <live-R7A-system-tree> <R7A-metadata.txt> <FarfarRemote-OS.apk> <bootanimation.zip> <output.ext4>" >&2
  exit 2
fi

repo=$(git rev-parse --show-toplevel)
builder="$repo/research/custom-rom/tools/create_r7a_system_image_poc.py"
source=$1
stock_tree=$2
r7a_tree=$3
metadata=$4
apk=$5
animation=$6
output=$(realpath -m -- "$7")

for item in "$source" "$stock_tree" "$r7a_tree" "$metadata" "$apk" "$animation"; do
  [[ -e "$item" ]] || { echo "Input does not exist: $item" >&2; exit 2; }
done
case "$output" in
  "$repo"/*) echo "Refusing to put proprietary-derived image data in Git: $output" >&2; exit 2 ;;
esac
[[ ! -e "$output" ]] || { echo "Refusing to overwrite output: $output" >&2; exit 2; }
[[ -n "${AAPT2_BIN:-}" && -x "$AAPT2_BIN" ]] || {
  echo "Set AAPT2_BIN to an executable Android SDK aapt2 binary." >&2; exit 2;
}

python3 "$builder" "$source" "$stock_tree" "$r7a_tree" "$metadata" "$apk" "$output" "$animation"
sha256sum "$output" > "$output.sha256"
printf 'checksum_file=%s.sha256\n' "$output"
printf 'classification=EXPERIMENTAL SYSTEM PARTITION EXT4; NOT A FLASHABLE FIRMWARE PACKAGE; NOT BOOT-TESTED\n'
