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
data_root=$(realpath -m -- "${FARFAR_DATA_ROOT:-/mnt/data/FarfarRemote-Research-POC}")
build_root="$data_root/builds/FarfarOS-v0.1"
tmp_root=$(realpath -m -- "${FARFAR_TMPDIR:-"$data_root/tmp"}")
source=$1
stock_tree=$2
r7a_tree=$3
metadata=$4
apk=$5
animation=$6
output=$(realpath -m -- "$7")

# Refuse to fall back to `/` if the data volume is not mounted.
probe=$data_root
while [[ ! -e "$probe" ]]; do
  parent=$(dirname -- "$probe")
  [[ "$parent" != "$probe" ]] || { echo "Cannot find a mounted filesystem for $data_root" >&2; exit 2; }
  probe=$parent
done
root_fs=$(stat -f -c '%d' /)
data_fs=$(stat -f -c '%d' "$probe")
[[ "$root_fs" != "$data_fs" ]] || {
  echo "Data root is on the system filesystem; refusing to build: $data_root" >&2; exit 2;
}

tmp_probe=$tmp_root
while [[ ! -e "$tmp_probe" ]]; do
  parent=$(dirname -- "$tmp_probe")
  [[ "$parent" != "$tmp_probe" ]] || { echo "Cannot find a mounted filesystem for temporary path $tmp_root" >&2; exit 2; }
  tmp_probe=$parent
done
tmp_fs=$(stat -f -c '%d' "$tmp_probe")
[[ "$tmp_fs" == "$data_fs" ]] || {
  echo "Temporary path must be on the same data filesystem: $tmp_root" >&2; exit 2;
}
free_bytes=$(df -PB1 "$probe" | awk 'END {print $4}')
(( free_bytes >= 5 * 1024 * 1024 * 1024 )) || {
  echo "Data filesystem needs at least 5 GiB free; currently ${free_bytes:-unknown} bytes: $probe" >&2; exit 2;
}

# Keep large images, staging data and helper-tool temporary files off `/`.
mkdir -p "$build_root" "$tmp_root"
export TMPDIR="$tmp_root" TEMP="$tmp_root" TMP="$tmp_root"

for item in "$source" "$stock_tree" "$r7a_tree" "$metadata" "$apk" "$animation"; do
  [[ -e "$item" ]] || { echo "Input does not exist: $item" >&2; exit 2; }
done
case "$output" in
  "$repo"/*) echo "Refusing to put proprietary-derived image data in Git: $output" >&2; exit 2 ;;
  "$build_root"/*) ;;
  *) echo "Output must be under $build_root to protect the system partition: $output" >&2; exit 2 ;;
esac
mkdir -p "$(dirname -- "$output")"
[[ ! -e "$output" ]] || { echo "Refusing to overwrite output: $output" >&2; exit 2; }
[[ -n "${AAPT2_BIN:-}" && -x "$AAPT2_BIN" ]] || {
  echo "Set AAPT2_BIN to an executable Android SDK aapt2 binary." >&2; exit 2;
}

python3 "$builder" "$source" "$stock_tree" "$r7a_tree" "$metadata" "$apk" "$output" "$animation"
sha256sum "$output" > "$output.sha256"
printf 'checksum_file=%s.sha256\n' "$output"
printf 'classification=EXPERIMENTAL SYSTEM PARTITION EXT4; NOT A FLASHABLE FIRMWARE PACKAGE; NOT BOOT-TESTED\n'
