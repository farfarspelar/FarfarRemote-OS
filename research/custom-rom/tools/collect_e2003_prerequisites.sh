#!/usr/bin/env bash
set -euo pipefail

# Read-only collection of E2003 ROM-build prerequisites.
# This script never reboots, roots, unlocks, reads block-device contents,
# writes to the phone, or stores a device log. Output is stdout only.

command -v adb >/dev/null 2>&1 || { echo "ERROR: adb is not installed" >&2; exit 1; }
adb start-server >/dev/null 2>&1 || true

device_serial="$(adb devices -l | awk '
  NR > 1 && $2 == "device" && $0 ~ /model:E2003([[:space:]]|$)/ { count++; serial=$1 }
  END { if (count == 1) print serial; else if (count > 1) exit 2; else exit 1 }
')" || {
  echo "ERROR: expected exactly one authorized USB device reporting model E2003" >&2
  exit 1
}

adb_device=(adb -s "$device_serial")
device_model="$("${adb_device[@]}" shell getprop ro.product.model 2>/dev/null | tr -d '\r')"
device_build="$("${adb_device[@]}" shell getprop ro.build.id 2>/dev/null | tr -d '\r')"
if [[ "$device_model" != "E2003" || "$device_build" != "25.0.A.2.31" ]]; then
  echo "ERROR: connected device is $device_model / $device_build; expected E2003 / 25.0.A.2.31" >&2
  exit 1
fi

section() { printf '\n--- %s ---\n' "$1"; }
prop() {
  local key="$1" value
  value="$("${adb_device[@]}" shell getprop "$key" 2>/dev/null | tr -d '\r')"
  printf '%s=%s\n' "$key" "$value"
}
read_remote() {
  local path="$1"
  "${adb_device[@]}" shell "cat '$path'" 2>&1 | tr -d '\r' || true
}

section "Verified device identity"
prop ro.product.model
prop ro.product.device
prop ro.product.board
prop ro.build.fingerprint
prop ro.build.version.release
prop ro.build.version.sdk
prop ro.build.id
prop ro.build.version.incremental
prop ro.semc.version.cust
prop ro.semc.version.cust_revision
prop ro.semc.version.sw
prop ro.semc.version.sw_variant
prop ro.mediatek.platform
prop ro.hardware
prop ro.product.cpu.abi
prop ro.bootloader

section "Kernel and CPU"
read_remote /proc/version
"${adb_device[@]}" shell 'cat /proc/cpuinfo' 2>&1 | tr -d '\r' | sed '/^[[:space:]]*Serial[[:space:]]*:/Id' || true
for cpu_property in possible present online offline; do
  printf 'cpu_%s=' "$cpu_property"
  read_remote "/sys/devices/system/cpu/$cpu_property"
done
for cpu_property in scaling_driver scaling_governor scaling_available_governors scaling_available_frequencies cpuinfo_min_freq cpuinfo_max_freq scaling_min_freq scaling_cur_freq; do
  printf 'cpu0_%s=' "$cpu_property"
  read_remote "/sys/devices/system/cpu/cpu0/cpufreq/$cpu_property"
done
printf 'kernel_config_path='; "${adb_device[@]}" shell 'ls -l /proc/config.gz 2>&1' | tr -d '\r' || true
printf 'kernel_cmdline_path='; "${adb_device[@]}" shell 'ls -l /proc/cmdline 2>&1' | tr -d '\r' || true

section "Memory and partition metadata (no partition contents)"
"${adb_device[@]}" shell 'cat /proc/meminfo' 2>&1 | tr -d '\r' | sed -n '1,12p' || true
read_remote /proc/partitions
"${adb_device[@]}" shell 'ls -l /dev/block/platform/mtk-msdc.0/by-name' 2>&1 | tr -d '\r' || true

section "Kernel module and Wi-Fi driver metadata"
"${adb_device[@]}" shell 'cat /proc/modules' 2>&1 | tr -d '\r' || true
"${adb_device[@]}" shell 'cat /sys/bus/platform/devices/180f0000.WIFI/uevent' 2>&1 | tr -d '\r' || true
"${adb_device[@]}" shell 'cat /sys/class/net/wlan0/uevent' 2>&1 | tr -d '\r' || true
"${adb_device[@]}" shell 'readlink /sys/class/net/wlan0/device/driver' 2>&1 | tr -d '\r' || true

section "Display, input and vendor HAL metadata"
prop ro.sf.lcd_density
prop ro.opengles.version
"${adb_device[@]}" shell 'for path in /system/lib/hw /system/vendor/lib/hw /system/lib/modules; do echo "[$path]"; ls -la "$path" 2>&1; done' 2>&1 | tr -d '\r' || true
"${adb_device[@]}" shell 'cat /proc/bus/input/devices' 2>&1 | tr -d '\r' | sed -E '/^(P: Phys=|U: Uniq=)/d' || true

section "Read-only limitations"
printf '%s\n' "No raw partition data was accessed. Empty or denied kernel interfaces above are reported as-is."
