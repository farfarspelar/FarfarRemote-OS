#!/usr/bin/env bash
set -euo pipefail

# Read-only E2003 /system metadata capture. Does not reboot or write to device.
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <output-file-outside-repository>" >&2
  exit 2
fi

command -v adb >/dev/null || { echo "adb is required." >&2; exit 2; }
out=$(realpath -m -- "$1")
repo=$(git rev-parse --show-toplevel)
case "$out" in "$repo"/*) echo "Refusing to store device metadata in the Git repository." >&2; exit 2;; esac
[[ ! -e "$out" ]] || { echo "Refusing to overwrite: $out" >&2; exit 2; }
mkdir -p "$(dirname -- "$out")"

tmp=$(mktemp "${TMPDIR:-/tmp}/e2003-system-metadata.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT
mapfile -t connected < <(adb devices | awk 'NR > 1 && $2 == "device" {print $1}')
[[ ${#connected[@]} -eq 1 ]] || {
  echo "Expected exactly one authorized ADB device; found ${#connected[@]}." >&2
  exit 1
}
serial=${connected[0]}

getprop() { adb -s "$serial" shell getprop "$1" | tr -d '\r'; }
model=$(getprop ro.product.device)
build=$(getprop ro.build.display.id)
cda=$(getprop ro.semc.version.cust)
revision=$(getprop ro.semc.version.cust_revision)
if [[ "$model" != E2003 || "$build" != 25.0.A.2.31 || "$cda" != 1293-7358 || "$revision" != R7A ]]; then
  echo "Refusing capture: attached handset is not the expected E2003 / 25.0.A.2.31 / 1293-7358 R7A." >&2
  exit 1
fi

{
  printf '# target_model=%s\n# target_build=%s\n# target_cda=%s\n# target_revision=%s\n' "$model" "$build" "$cda" "$revision"
  adb -s "$serial" shell 'ls -laRZ /system'
} > "$tmp"
mv -- "$tmp" "$out"
trap - EXIT
printf 'Read-only metadata saved: %s\n' "$out"
printf 'SHA-256: %s\n' "$(sha256sum "$out" | cut -d ' ' -f1)"
