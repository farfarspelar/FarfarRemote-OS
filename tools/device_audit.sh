#!/usr/bin/env bash
set -euo pipefail

# Read-only Sony Xperia E2003 audit. Runs adb shell queries only; it never changes device state.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_BASE="$ROOT_DIR/reports/device_audit"
ADB_BIN="${ADB:-adb}"

die() { printf 'device_audit: %s\n' "$*" >&2; exit 1; }
command -v "$ADB_BIN" >/dev/null 2>&1 || die "adb not found (set ADB=/path/to/adb)"
mkdir -p "$OUT_BASE"
mapfile -t ONLINE < <("$ADB_BIN" devices | awk 'NR > 1 && $2 == "device" {print $1}')
((${#ONLINE[@]} == 1)) || die "expected exactly one authorized adb device; found ${#ONLINE[@]} (run adb devices)"
SERIAL="${ONLINE[0]}"
adbsh() { "$ADB_BIN" -s "$SERIAL" shell "$@"; }

MODEL="$(adbsh getprop ro.product.model | tr -d '\r')"
DEVICE="$(adbsh getprop ro.product.device | tr -d '\r')"
PRODUCT="$(adbsh getprop ro.build.product | tr -d '\r')"
if [[ "$MODEL" != *E2003* && "$DEVICE" != *E2003* && "$PRODUCT" != *E2003* ]]; then
  die "device identity mismatch: model='$MODEL' device='$DEVICE' product='$PRODUCT'; no audit collected"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUT_BASE/${STAMP}_${SERIAL}"
mkdir -m 700 "$OUT"
printf 'FarfarRemote read-only device audit\nUTC: %s\nADB serial: %s\nModel: %s\nDevice: %s\nProduct: %s\n' \
  "$STAMP" "$SERIAL" "$MODEL" "$DEVICE" "$PRODUCT" > "$OUT/README.txt"

capture() {
  local name="$1"; shift
  { printf '$ adb shell'; printf ' %q' "$@"; printf '\n'; adbsh "$@" 2>&1 || true; } > "$OUT/$name.txt"
}
capture getprop getprop
capture packages_system pm list packages -s -f
capture packages_third_party pm list packages -3 -f
capture packages_all pm list packages -f
capture package_manager dumpsys package
capture processes ps
capture top top -n 1 -m 100
capture memory dumpsys meminfo
capture memoryinfo_proc cat /proc/meminfo
capture uptime cat /proc/uptime
capture boot_completed getprop sys.boot_completed
capture boot_events logcat -d -b events -v time
capture services_list service list
capture activity_services dumpsys activity services
capture activity_processes dumpsys activity processes
capture activity_broadcasts dumpsys activity broadcasts
capture connectivity dumpsys connectivity
capture wifi dumpsys wifi
capture power dumpsys power
capture battery dumpsys battery
capture mounts cat /proc/mounts
capture filesystems cat /proc/filesystems
capture disk df
capture init_processes cat /init.rc
capture init_device cat /init.mt6732.rc
capture init_hardware cat /init.target.rc
capture init_files find /system/etc/init -maxdepth 2 -type f
capture permissions ls -l /system/etc/permissions
capture framework_files ls -l /system/framework
capture system_build_prop cat /system/build.prop
capture logcat_main logcat -d -b main -v time
capture logcat_system logcat -d -b system -v time

printf 'Audit complete: %s\nNo settings, packages, files, or partitions were modified.\n' "$OUT" | tee -a "$OUT/README.txt"
printf 'Analyze with: python3 %q %q\n' "$ROOT_DIR/tools/analyze_device_audit.py" "$OUT"
