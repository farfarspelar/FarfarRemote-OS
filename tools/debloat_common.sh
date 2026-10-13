#!/usr/bin/env bash
set -euo pipefail

DR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DR_ADB="${ADB:-adb}"
DR_AUDIT_ROOT="$DR_ROOT/reports/device_audit"
DR_CANDIDATES="$DR_ROOT/tools/debloat_packages.tsv"
DR_AUDIT_DIR=""
DR_SERIAL=""
DR_STATE=""
DR_DISPLAY_ID=""
DR_ANDROID_RELEASE=""
DR_ANDROID_API=""

dr_die() { printf 'FarfarRemote Debloat: %s\n' "$*" >&2; exit 1; }
dr_latest_audit() {
  local f
  f="$(find "$DR_AUDIT_ROOT" -mindepth 2 -maxdepth 2 -name README.txt -printf '%T@ %h\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"
  [[ -n "$f" && -f "$f/README.txt" ]] || dr_die "no reports/device_audit/* audit found"
  DR_AUDIT_DIR="$f"
  DR_SERIAL="$(sed -n 's/^ADB serial: //p' "$f/README.txt" | head -1 | tr -d '\r')"
  [[ -n "$DR_SERIAL" ]] || dr_die "audit has no ADB serial"
  grep -q '^Model: E2003$' "$f/README.txt" || dr_die "latest audit does not identify model E2003"
  [[ -f "$f/getprop.txt" ]] || dr_die "audit has no getprop snapshot for firmware pinning"
  DR_DISPLAY_ID="$(awk -F'[][]' '$2=="ro.build.display.id" {print $4; exit}' "$f/getprop.txt" | tr -d '\r')"
  DR_ANDROID_RELEASE="$(awk -F'[][]' '$2=="ro.build.version.release" {print $4; exit}' "$f/getprop.txt" | tr -d '\r')"
  DR_ANDROID_API="$(awk -F'[][]' '$2=="ro.build.version.sdk" {print $4; exit}' "$f/getprop.txt" | tr -d '\r')"
  [[ -n "$DR_DISPLAY_ID" && "$DR_ANDROID_RELEASE" == 4.4.4 && "$DR_ANDROID_API" == 19 ]] || dr_die "audit firmware is incomplete or not Android 4.4.4/API 19"
  DR_STATE="$DR_ROOT/reports/debloat/$DR_SERIAL"
  mkdir -p "$DR_STATE/metrics"
}
dr_device_check() {
  command -v "$DR_ADB" >/dev/null 2>&1 || dr_die "adb not found (set ADB=/path/to/adb)"
  mapfile -t dr_online < <("$DR_ADB" devices | awk 'NR > 1 && $2 == "device" {print $1}')
  ((${#dr_online[@]} == 1)) || dr_die "expected exactly one authorized ADB device; found ${#dr_online[@]}"
  [[ "${dr_online[0]}" == "$DR_SERIAL" ]] || dr_die "connected serial '${dr_online[0]}' differs from audited E2003 '$DR_SERIAL'"
  local model device product display release api
  model="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.product.model | tr -d '\r')"
  device="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.product.device | tr -d '\r')"
  product="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.build.product | tr -d '\r')"
  display="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.build.display.id | tr -d '\r')"
  release="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.build.version.release | tr -d '\r')"
  api="$("$DR_ADB" -s "$DR_SERIAL" shell getprop ro.build.version.sdk | tr -d '\r')"
  if [[ "$model" != *E2003* && "$device" != *E2003* && "$product" != *E2003* ]]; then
    dr_die "identity check failed: model='$model' device='$device' product='$product'"
  fi
  [[ "$display" == "$DR_DISPLAY_ID" && "$release" == "$DR_ANDROID_RELEASE" && "$api" == "$DR_ANDROID_API" ]] || dr_die "firmware changed since audit: current '$display' Android $release/API $api; expected '$DR_DISPLAY_ID' Android $DR_ANDROID_RELEASE/API $DR_ANDROID_API"
  printf 'ADB identity OK: %s — %s / %s / %s — %s Android %s/API %s\n' "$DR_SERIAL" "$model" "$device" "$product" "$display" "$release" "$api"
}
# Package selection loops read the candidate TSV from stdin. Keep remote shell
# commands from inheriting that stream, or an ADB invocation can consume later rows.
dr_shell() { "$DR_ADB" -s "$DR_SERIAL" shell "$@" </dev/null; }
dr_log_event() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" "${4:-}" >> "$DR_STATE/actions.tsv"
}
dr_log_phase() {
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "${3:-}" >> "$DR_STATE/phases.tsv"
}
dr_latest_phase_status() {
  awk -F'\t' -v phase="$1" '$2==phase {s=$3} END {print s}' "$DR_STATE/phases.tsv" 2>/dev/null || true
}
dr_latest_package_status() {
  awk -F'\t' -v group="$1" -v package="$2" '$2=="DISABLE" && $3==group && $4==package {s=$5} $2=="RESTORE" && $3==group && $4==package {s=$5} END {print s}' "$DR_STATE/actions.tsv" 2>/dev/null || true
}
dr_metric_snapshot() {
  local label="$1" stamp out i
  local app_processes
  # Measurements belong to the dedicated OS track. A running regular-App flavor
  # adds its own process load and makes OS before/after comparisons misleading.
  app_processes="$(dr_shell ps 2>/dev/null | awk 'NR > 1 && $NF ~ /^org\.farfarremote\.app(:|$)/ { print $NF }' | sort -u)"
  if [[ -n "$app_processes" ]]; then
    dr_die "OS metrics require FarfarRemote App to be closed; active App process(es): ${app_processes//$'\n'/, }. Close the App flavor without changing the OS installation, then retry."
  fi
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  out="$DR_STATE/metrics/${stamp}_${label}"
  mkdir -m 700 "$out"
  dr_device_check > "$out/device_identity.txt"
  {
    printf '$ adb shell dumpsys meminfo\n'; dr_shell dumpsys meminfo 2>&1 || true
  } > "$out/memory.txt"
  {
    printf '$ adb shell cat /proc/meminfo\n'; dr_shell cat /proc/meminfo 2>&1 || true
  } > "$out/meminfo_proc.txt"
  {
    printf '$ adb shell ps\n'; dr_shell ps 2>&1 || true
  } > "$out/processes.txt"
  {
    printf '$ adb shell cat /proc/stat\n'; dr_shell cat /proc/stat 2>&1 || true
  } > "$out/proc_stat.txt"
  {
    printf '$ adb shell cat /proc/uptime\n'; dr_shell cat /proc/uptime 2>&1 || true
  } > "$out/uptime.txt"
  {
    printf '$ adb shell dumpsys battery\n'; dr_shell dumpsys battery 2>&1 || true
  } > "$out/battery.txt"
  {
    printf '$ adb shell dumpsys wifi\n'; dr_shell dumpsys wifi 2>&1 || true
  } > "$out/wifi.txt"
  {
    printf '$ adb shell dumpsys connectivity\n'; dr_shell dumpsys connectivity 2>&1 || true
  } > "$out/connectivity.txt"
  {
    printf '$ adb shell logcat -d -b events -v time\n'; dr_shell logcat -d -b events -v time 2>&1 || true
  } > "$out/boot_events.txt"
  for i in 1 2 3 4 5; do
    dr_device_check >/dev/null
    { printf '$ adb shell top -n 1 -m 30 (sample %s)\n' "$i"; dr_shell top -n 1 -m 30 2>&1 || true; } > "$out/top_${i}.txt"
    dr_shell cat /proc/stat > "$out/proc_stat_${i}.txt" 2>&1 || true
    [[ "$i" == 5 ]] || sleep 5
  done
  cat > "$out/README.txt" <<EOF
Metric snapshot: $label
UTC: $stamp
Device: $DR_SERIAL (E2003 verified immediately before collection)
Read-only commands only. CPU is sampled five times at five-second intervals.
PSS active and cached OOM groups are recorded separately in memory.txt.
The regular FarfarRemote App process must be closed for OS-track metrics; this is checked before capture.
The five-minute idle period and matching screen/network/charger conditions must be prepared manually.
Cold-boot duration must be recorded manually with --record-boot-seconds.
EOF
  printf '%s\n' "$out"
}

dr_package_installed() {
  # Consume the complete ADB stream: grep -q can close the pipe early and make
  # adb/tr return SIGPIPE under set -o pipefail, falsely reporting a package missing.
  dr_shell pm list packages | tr -d '\r' | grep -Fx "package:$1" >/dev/null
}
dr_package_disabled() {
  dr_shell pm list packages -d | tr -d '\r' | grep -Fx "package:$1" >/dev/null
}
dr_protected_package() {
  case "$1" in
    android|android.res.overlay|org.farfarremote|com.android.systemui|com.android.settings|com.android.providers.settings|com.android.shell|com.android.packageinstaller|com.android.inputdevices|com.android.phone|com.android.providers.telephony|com.android.incallui|com.android.bluetooth|com.mediatek.bluetooth|com.android.externalstorage|com.android.providers.media|com.android.providers.downloads|com.android.providers.downloads.ui|com.android.defcontainer|com.android.keychain|com.sonyericsson.home|com.sonyericsson.home.res.overlay|com.sonyericsson.uxp|com.sonyericsson.textinput.uxp|com.sonymobile.touchscreen.touchfilter|com.sonymobile.superstamina|com.sonymobile.cameracommon|com.sonymobile.autopairing|com.sonymobile.runtimeskinning.core|com.sonyericsson.android.bootinfo|com.sonymobile.enterprise.service|com.sonyericsson.oemCryptoReceiver|com.mediatek|com.mediatek.providers.drm|com.sonyericsson.android.drm.services)
      return 0 ;;
    *) return 1 ;;
  esac
}

dr_restore_group() {
  local group="$1" package status g entry
  local -a entries=()
  if [[ "$group" == "ALL" ]]; then
    mapfile -t entries < <(awk -F'\t' '$2=="DISABLE" && ($5=="DISABLED" || $5=="PENDING") {print $3 "\t" $4}' "$DR_STATE/actions.tsv" 2>/dev/null | tac)
  else
    mapfile -t entries < <(awk -F'\t' -v g="$group" '$2=="DISABLE" && $3==g && ($5=="DISABLED" || $5=="PENDING") {print $3 "\t" $4}' "$DR_STATE/actions.tsv" 2>/dev/null | tac)
  fi
  local -A seen=()
  for entry in "${entries[@]}"; do
    IFS=$'\t' read -r g package <<< "$entry"
    [[ -n "$package" && -z "${seen[$g:$package]:-}" ]] || continue
    seen[$g:$package]=1
    status="$(dr_latest_package_status "$g" "$package")"
    [[ "$status" == "DISABLED" || "$status" == "PENDING" ]] || continue
    dr_device_check
    if dr_package_disabled "$package"; then
      dr_shell pm enable --user 0 "$package"
      dr_device_check
      if dr_package_disabled "$package"; then
        dr_log_event RESTORE "$g" "$package" ERROR "still listed disabled after pm enable"
        return 1
      fi
      dr_log_event RESTORE "$g" "$package" RESTORED "pm enable --user 0"
    else
      dr_log_event RESTORE "$g" "$package" ALREADY_ENABLED "no change"
    fi
  done
  dr_device_check
}

dr_baseline_exists() { find "$DR_STATE/metrics" -maxdepth 1 -type d -name '*_baseline' -print -quit | grep -q .; }
