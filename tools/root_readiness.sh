#!/usr/bin/env bash
# Read-only readiness check for the Sony Xperia E4g E2003.
# This script never reboots, unlocks, roots, flashes, or changes device settings.
set -euo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
command -v adb >/dev/null 2>&1 || fail "adb is not installed or not on PATH"

mapfile -t devices < <(adb devices | awk 'NR > 1 && $2 == "device" { print $1 }')
if [[ ${#devices[@]} -ne 1 ]]; then
  fail "Expected exactly one authorized ADB device; found ${#devices[@]}. Check 'adb devices' locally."
fi
serial=${devices[0]}

getprop() { adb -s "$serial" shell getprop "$1" 2>/dev/null | tr -d '\r'; }
model=$(getprop ro.product.model)
device=$(getprop ro.product.device)
firmware=$(getprop ro.build.display.id)
fingerprint=$(getprop ro.build.fingerprint)
api=$(getprop ro.build.version.sdk)
id_line=$(adb -s "$serial" shell id 2>/dev/null | tr -d '\r')
uid=$(sed -n 's/^uid=\([0-9][0-9]*\).*/\1/p' <<<"$id_line")

printf 'FarfarRemote OS root readiness (read-only)\n'
printf 'Model: %s\nDevice: %s\nFirmware: %s\nAndroid API: %s\n' "$model" "$device" "$firmware" "$api"
printf 'Build fingerprint: %s\n' "$fingerprint"

if [[ "$model" != "E2003" || "$device" != "E2003" || "$fingerprint" != Sony/E2003/E2003:* ]]; then
  printf 'Device match: FAIL (expected exact Sony E2003 identity)\n'
  exit 2
fi
printf 'Device match: PASS (exact E2003)\n'

printf 'ADB shell identity: %s\n' "$id_line"
if [[ "$uid" == "0" ]]; then
  printf 'Root in current ADB shell: YES (uid 0)\n'
else
  printf 'Root in current ADB shell: NO (uid %s)\n' "${uid:-unknown}"
fi

su_path=$(adb -s "$serial" shell 'command -v su' 2>/dev/null | tr -d '\r' || true)
if [[ -n "$su_path" ]]; then
  printf 'su command on PATH: %s (presence does not prove it grants root)\n' "$su_path"
else
  printf 'su command on PATH: no\n'
fi

disabled_list=$(adb -s "$serial" shell pm list packages -d 2>/dev/null | tr -d '\r' | sed 's/^package://' | sed '/^$/d' || true)
if [[ -n "$disabled_list" ]]; then
  printf 'Disabled Android packages (pre-existing state; unchanged by this check):\n%s\n' "$disabled_list"
else
  printf 'Disabled Android packages: none reported\n'
fi
printf 'System image / package changes: none performed\n'

if command -v fastboot >/dev/null 2>&1; then
  mapfile -t fb_devices < <(fastboot devices 2>/dev/null | awk 'NF >= 2 { print $1 }')
  if [[ ${#fb_devices[@]} -eq 0 ]]; then
    printf 'Fastboot: no device currently attached in fastboot mode (not entered by this script)\n'
  else
    printf 'Fastboot: device present; read-only properties follow\n'
    # Query only the connected fastboot endpoint. Do not print its USB serial.
    product=$(fastboot -s "${fb_devices[0]}" getvar product 2>&1 | sed -n 's/.*product: *//p' | tr -d '\r' | tail -n 1 || true)
    unlocked=$(fastboot -s "${fb_devices[0]}" getvar unlocked 2>&1 | sed -n 's/.*unlocked: *//p' | tr -d '\r' | tail -n 1 || true)
    printf 'Fastboot product: %s\n' "${product:-unavailable}"
    printf 'Fastboot unlocked property: %s\n' "${unlocked:-unavailable (not proof of locked state)}"
  fi
else
  printf 'Fastboot: tool unavailable\n'
fi

printf '\nInterpretation: bootloader unlock and Android root are separate states. This check does not establish that a specific root method or recovery image is safe for E2003 firmware %s.\n' "$firmware"
