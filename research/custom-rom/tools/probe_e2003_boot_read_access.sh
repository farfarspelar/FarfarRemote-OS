#!/usr/bin/env bash
set -uo pipefail

# Read-only probe: determines whether ordinary ADB shell can read the first
# four bytes of the E2003 boot and FOTA/recovery block devices. Data is sent
# directly to the device's /dev/null and is never copied to the host.
# This script never reboots, roots, unlocks, changes settings, or writes blocks.

command -v adb >/dev/null 2>&1 || { echo "ERROR: adb is not installed" >&2; exit 1; }
adb start-server >/dev/null 2>&1 || true

device_serial="$(adb devices -l | awk '
  NR > 1 && $2 == "device" && $0 ~ /model:E2003([[:space:]]|$)/ { count++; serial=$1 }
  END { if (count == 1) print serial; else if (count > 1) exit 2; else exit 1 }
')" || {
  echo "ERROR: expected exactly one authorized USB device reporting model E2003" >&2
  exit 1
}

device=(adb -s "$device_serial")
model="$("${device[@]}" shell getprop ro.product.model 2>/dev/null | tr -d '\r')"
build="$("${device[@]}" shell getprop ro.build.id 2>/dev/null | tr -d '\r')"
if [[ "$model" != "E2003" || "$build" != "25.0.A.2.31" ]]; then
  echo "ERROR: connected device is $model / $build; expected E2003 / 25.0.A.2.31" >&2
  exit 1
fi

echo "Verified target: Sony E2003 / Android build 25.0.A.2.31"
echo "Probe reads at most four bytes and discards them on-device. No image is saved."
for partition in boot fotakernel; do
  path="/dev/block/platform/mtk-msdc.0/by-name/$partition"
  echo "[$partition]"
  "${device[@]}" shell "dd if='$path' of=/dev/null bs=4 count=1 2>&1; echo read_exit=\$?" 2>&1 | tr -d '\r'
done
