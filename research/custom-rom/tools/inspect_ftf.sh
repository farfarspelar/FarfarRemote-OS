#!/usr/bin/env bash
# Read-only Sony FTF container integrity/listing check. Never extracts or flashes.
set -euo pipefail

usage() { echo "Usage: $0 firmware.ftf [expected-sha256]" >&2; exit 2; }
[[ $# -ge 1 && $# -le 2 ]] || usage
ftf=$1
[[ -f "$ftf" && -r "$ftf" ]] || { echo "ERROR: FTF is not a readable regular file" >&2; exit 1; }
command -v sha256sum >/dev/null 2>&1 || { echo "ERROR: sha256sum is required" >&2; exit 1; }
command -v unzip >/dev/null 2>&1 || { echo "ERROR: unzip is required" >&2; exit 1; }

actual=$(sha256sum -- "$ftf" | awk '{print $1}')
printf 'Input: %s\nSHA-256: %s\n' "$(basename -- "$ftf")" "$actual"
if [[ $# -eq 2 ]]; then
  expected=${2,,}
  [[ "$expected" =~ ^[0-9a-f]{64}$ ]] || { echo "ERROR: expected hash must be 64 hexadecimal characters" >&2; exit 2; }
  if [[ "$actual" != "$expected" ]]; then
    echo 'HASH CHECK: FAIL' >&2
    exit 1
  fi
  echo 'HASH CHECK: PASS (matches supplied expected SHA-256)'
else
  echo 'HASH CHECK: no expected hash supplied; computed value alone does not prove provenance'
fi

echo 'ZIP integrity check:'
unzip -tq -- "$ftf"
echo 'ZIP listing (names only):'
unzip -Z1 -- "$ftf"
echo
echo 'Note: a valid ZIP and matching optional hash do not establish exact model/CDA compatibility.'
echo 'No extraction, device access, or flashing was performed.'
