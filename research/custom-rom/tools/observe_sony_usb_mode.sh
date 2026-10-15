#!/usr/bin/env bash
# Passive USB enumeration helper for an owner-operated Sony Flashmode check.
# Does not invoke adb, fastboot, Flashtool, or write to any device.
set -euo pipefail

timeout_seconds=${1:-120}
if ! [[ "$timeout_seconds" =~ ^[0-9]+$ ]] || (( timeout_seconds < 1 || timeout_seconds > 900 )); then
  printf 'Usage: %s [timeout-seconds: 1..900]\n' "$0" >&2
  exit 2
fi
if ! command -v lsusb >/dev/null 2>&1; then
  printf 'lsusb is required (Linux Mint package: usbutils).\n' >&2
  exit 2
fi

declare -A baseline=()
while IFS= read -r id; do
  [[ $id =~ ^0fce:[[:xdigit:]]+$ ]] || continue
  baseline["$id"]=$(( ${baseline["$id"]:-0} + 1 ))
done < <(lsusb | awk '{print $6}')

printf 'Passive Sony USB observer: %ss timeout. No device commands will be sent.\n' "$timeout_seconds"
printf 'Existing Sony USB device count: %s\n' "${#baseline[@]}"
printf 'When ready, follow the E2003 Flashmode key sequence; stop if the phone state is unclear.\n'

declare -A seen=()
for ((elapsed=0; elapsed<timeout_seconds; elapsed++)); do
  declare -A current=()
  while IFS= read -r id; do
    [[ $id =~ ^0fce:[[:xdigit:]]+$ ]] || continue
    current["$id"]=$(( ${current["$id"]:-0} + 1 ))
  done < <(lsusb | awk '{print $6}')

  for id in "${!current[@]}"; do
    count=${current[$id]}
    old_count=${baseline[$id]:-0}
    reported_count=${seen[$id]:-0}
    if (( count > old_count && count > reported_count )); then
      printf 'New Sony USB VID:PID observed: %s (count=%s).\n' "$id" "$count"
      printf 'This is enumeration only; it does not prove E2003 identity, Flashmode, or restore capability.\n'
      exit 0
    fi
  done
  seen=()
  for id in "${!current[@]}"; do seen[$id]=${current[$id]}; done
  sleep 1
done

printf 'No new Sony USB VID:PID observed within %ss. Phone state was not changed by this script.\n' "$timeout_seconds"
