#!/usr/bin/env bash
set -euo pipefail

readonly expected_size=2097152000
readonly expected_sha256=cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d
readonly expected_product=E2003
readonly expected_partition_size=0x7d000000
readonly fastboot_vendor=0x0fce

fail() { printf 'PREFLIGHT FAIL: %s\n' "$*" >&2; exit 1; }

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <FarfarOS-v0.1-system.ext4>" >&2
  echo "Read-only checks only; this script never flashes, boots, erases or reboots." >&2
  exit 2
fi

image=$(realpath -- "$1")
[[ -f "$image" ]] || fail "system image is not a regular file: $image"
size=$(stat -c '%s' "$image")
[[ "$size" == "$expected_size" ]] || fail "image size $size does not match expected $expected_size bytes"
actual_sha=$(sha256sum "$image" | awk '{print $1}')
[[ "$actual_sha" == "$expected_sha256" ]] || fail "image SHA-256 does not match the reviewed artifact"
image_type=$(file -b "$image")
[[ "$image_type" == *ext4* ]] || fail "image is not identified as ext4: $image_type"
printf 'Image: size=%s bytes, ext4, SHA-256=%s\n' "$size" "$actual_sha"

fastboot_bin=${FASTBOOT_BIN:-fastboot}
command -v "$fastboot_bin" >/dev/null 2>&1 || fail "fastboot executable not found: $fastboot_bin"
devices=$($fastboot_bin -i "$fastboot_vendor" devices 2>&1) || fail "could not enumerate Fastboot devices"
device_count=$(printf '%s\n' "$devices" | awk 'NF {count++} END {print count+0}')
[[ "$device_count" == 1 ]] || fail "expected exactly one Fastboot device; found $device_count"

getvar() {
  local variable=$1 output
  output=$($fastboot_bin -i "$fastboot_vendor" getvar "$variable" 2>&1) || true
  printf '%s' "$output"
}

product_output=$(getvar product)
product=$(printf '%s\n' "$product_output" | sed -nE 's/.*product:[[:space:]]*([^[:space:]]+).*/\1/p' | head -n1)
[[ "$product" == "$expected_product" ]] || fail "Fastboot product is '${product:-unknown}', expected E2003"
printf 'Fastboot product: %s\n' "$product"

size_output=$(getvar partition-size:system)
partition_size=$(printf '%s\n' "$size_output" | sed -nE 's/.*partition-size:system:[[:space:]]*(0x[[:xdigit:]]+).*/\1/ip' | head -n1 | tr '[:upper:]' '[:lower:]')
[[ "$partition_size" == "$expected_partition_size" ]] || fail "system partition size is '${partition_size:-unknown}', expected $expected_partition_size"
printf 'Fastboot system partition size: %s\n' "$partition_size"

bootloader_output=$(getvar version-bootloader)
bootloader=$(printf '%s\n' "$bootloader_output" | sed -nE 's/.*version-bootloader:[[:space:]]*(.*)$/\1/ip' | head -n1 | sed 's/[[:space:]]*$//')
[[ "$bootloader" == *'1290-9780 S1_Boot_MT6732_TC9PRA_9'* ]] || fail "bootloader identity is '${bootloader:-unknown}', expected the reviewed E2003 S1 bootloader"
printf 'Fastboot bootloader: %s\n' "$bootloader"

unlock_output=$(getvar unlocked)
unlocked=$(printf '%s\n' "$unlock_output" | sed -nE 's/.*unlocked:[[:space:]]*([^[:space:]]+).*/\1/ip' | head -n1 | tr '[:upper:]' '[:lower:]')
[[ "$unlocked" =~ ^(yes|true|1)$ ]] || fail "bootloader unlock state is not positively confirmed by Fastboot"
printf 'Fastboot unlocked: %s\n' "$unlocked"

printf '\nREAD-ONLY PREFLIGHT PASSED. No device write or reboot was attempted.\n'
printf 'This result is not authorization to flash; review the experiment proposal and obtain separate approval first.\n'
