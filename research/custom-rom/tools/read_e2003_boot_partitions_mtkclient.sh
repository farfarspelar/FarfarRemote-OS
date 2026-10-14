#!/usr/bin/env bash
set -euo pipefail

# Read-only MTKClient wrapper for the E2003 boot and fotakernel partitions.
# It has no argument passthrough and invokes only the `r` subcommand.
# MTKClient may upload a temporary loader to RAM and may reset the handset.
# It never calls MTKClient write, erase, format, unlock, or firmware commands.

EXPECTED_MTKCLIENT_COMMIT="7cb40e727727dfe3faa065eefb29b16ed29bbdf1"
EXPECTED_PARTITION_BYTES="33554432"
ROOT_DIR="$(git rev-parse --show-toplevel)"

usage() {
  cat >&2 <<'EOF'
Usage: read_e2003_boot_partitions_mtkclient.sh MTKCLIENT_DIR PYTHON OUTPUT_DIR

MTKCLIENT_DIR must be a clean checkout at the pinned reviewed commit.
PYTHON must be the Python executable in an isolated environment with MTKClient CLI dependencies.
OUTPUT_DIR must be a new directory outside the repository. The handset must already be in
a Sony/MediaTek BootROM mode that MTKClient supports. This helper does not enter BootROM mode.
EOF
  exit 2
}

[[ $# -eq 3 ]] || usage
MTKCLIENT_DIR="$(realpath "$1")"
PYTHON="$(realpath "$2")"
OUTPUT_DIR="$(realpath -m "$3")"

[[ -x "$PYTHON" ]] || { echo "ERROR: Python executable missing or not executable" >&2; exit 2; }
[[ -f "$MTKCLIENT_DIR/mtk.py" ]] || { echo "ERROR: mtk.py not found in MTKCLIENT_DIR" >&2; exit 2; }
[[ -d "$OUTPUT_DIR" && -z "$(find "$OUTPUT_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]] || {
  echo "ERROR: OUTPUT_DIR must exist and be empty" >&2
  exit 2
}
case "$OUTPUT_DIR/" in
  "$ROOT_DIR/"*) echo "ERROR: OUTPUT_DIR must be outside the Git repository" >&2; exit 2 ;;
esac

actual_commit="$(git -C "$MTKCLIENT_DIR" rev-parse HEAD)"
[[ "$actual_commit" == "$EXPECTED_MTKCLIENT_COMMIT" ]] || {
  echo "ERROR: unreviewed MTKClient commit: $actual_commit" >&2
  exit 2
}
[[ -z "$(git -C "$MTKCLIENT_DIR" status --porcelain)" ]] || {
  echo "ERROR: MTKClient checkout has local modifications" >&2
  exit 2
}

if command -v adb >/dev/null 2>&1 && adb devices | awk 'NR > 1 && $2 == "device" { found = 1 } END { exit found ? 0 : 1 }'; then
  echo "ERROR: an authorized Android ADB device is still online; power it down and enter BootROM first" >&2
  exit 3
fi

# Refuse to run unless exactly one Sony BootROM VID:PID used by MTKClient is present.
# Generic MediaTek and other Sony model IDs are deliberately not accepted. The current
# Android ADB identity (Sony 0fce:51cb) is also deliberately not accepted.
device_count="$("$PYTHON" - <<'PY'
import usb.core

allowed = {(0x0FCE, 0xF200)}
matches = [d for d in usb.core.find(find_all=True) if (d.idVendor, d.idProduct) in allowed]
for d in matches:
    print(f"MATCH {d.idVendor:04x}:{d.idProduct:04x}")
print(len(matches))
PY
)"
match_count="${device_count##*$'\n'}"
[[ "$match_count" == "1" ]] || {
  echo "ERROR: expected exactly one supported Sony/MediaTek BootROM USB device; found $match_count" >&2
  echo "$device_count" | sed '$d' >&2
  exit 3
}

tmp_dir="$(mktemp -d "$OUTPUT_DIR/.e2003-read.XXXXXX")"
capture_complete=0
cleanup() {
  rm -rf -- "$tmp_dir"
  if [[ "$capture_complete" != "1" ]]; then
    rm -f -- "$OUTPUT_DIR/boot.bin" "$OUTPUT_DIR/fotakernel.bin" "$OUTPUT_DIR/SHA256SUMS.txt" "$OUTPUT_DIR/READ_ONLY_CAPTURE.txt"
  fi
}
trap cleanup EXIT

for partition in boot fotakernel; do
  echo "Reading only partition: $partition"
  (cd "$MTKCLIENT_DIR" && PYTHONPATH="$MTKCLIENT_DIR" "$PYTHON" mtk.py r "$partition" "$tmp_dir/$partition.bin")
  actual_bytes="$(stat -c '%s' "$tmp_dir/$partition.bin")"
  [[ "$actual_bytes" == "$EXPECTED_PARTITION_BYTES" ]] || {
    echo "ERROR: $partition size $actual_bytes differs from expected $EXPECTED_PARTITION_BYTES; output discarded" >&2
    exit 4
  }
  mv -- "$tmp_dir/$partition.bin" "$OUTPUT_DIR/$partition.bin"
done

(
  cd "$OUTPUT_DIR"
  sha256sum boot.bin fotakernel.bin > SHA256SUMS.txt
)

cat > "$OUTPUT_DIR/READ_ONLY_CAPTURE.txt" <<EOF
Device previously identified in Android as Sony Xperia E2003 / 25.0.A.2.31 / 1293-7358 R7A.
MTKClient commit: $EXPECTED_MTKCLIENT_COMMIT
Operation: read-only partition reads of boot and fotakernel; no partition writes were requested.
Expected and observed partition byte length: $EXPECTED_PARTITION_BYTES each.
Capture contents are private device firmware; do not publish or commit them.
EOF

capture_complete=1
echo "Read-only capture complete. Protect OUTPUT_DIR and verify SHA256SUMS.txt."
echo "The files are not approved firmware/recovery artifacts until independently inspected."
