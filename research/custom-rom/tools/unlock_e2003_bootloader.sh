#!/usr/bin/env bash
# One-operation helper for the explicitly authorized Sony E2003 unlock.
# The unlock code is read without echo and is never written to a file or log.
set -euo pipefail
set +x

adb_bin="${ADB:-adb}"
fastboot_bin="${FASTBOOT:-fastboot}"
expected_product='E2003'
expected_bootloader='1290-9780 S1_Boot_MT6732_TC9PRA_9'
approval_text='UNLOCK E2003; erase user data; permanently lose DRM keys'

fail() { printf 'STOP: %s\n' "$1" >&2; exit 1; }

command -v "$adb_bin" >/dev/null 2>&1 || fail "ADB not found: $adb_bin"
command -v "$fastboot_bin" >/dev/null 2>&1 || fail "Fastboot not found: $fastboot_bin"

printf '%s\n' 'Sony Xperia E4g E2003 bootloader unlock' \
  'This performs a factory reset. Sony says DRM security keys cannot be restored.' \
  'Unlocking does not install FarfarOS and does not grant root by itself.' \
  'Enter the exact authorization phrase below to continue.'
printf 'Authorization: '
IFS= read -r confirmation || fail 'Could not read confirmation.'
[[ "$confirmation" == "$approval_text" ]] || fail 'Authorization phrase did not match.'

printf 'Sony unlock code (input hidden): '
IFS= read -r -s unlock_code || fail 'Could not read unlock code.'
printf '\n'
[[ "$unlock_code" =~ ^[[:alnum:]]{1,64}$ ]] || fail 'Code must contain only letters/digits (1-64 characters).'

adb_state=$("$adb_bin" get-state 2>/dev/null || true)
[[ "$adb_state" == device ]] || fail 'Expected the phone in normal Android with ADB authorized.'
device_model=$("$adb_bin" -d shell getprop ro.product.model | tr -d '\r')
device_code=$("$adb_bin" -d shell getprop ro.product.device | tr -d '\r')
device_fingerprint=$("$adb_bin" -d shell getprop ro.build.fingerprint | tr -d '\r')
customization=$("$adb_bin" -d shell getprop ro.semc.version.cust | tr -d '\r')
custom_revision=$("$adb_bin" -d shell getprop ro.semc.version.cust_revision | tr -d '\r')
[[ "$device_model" == "$expected_product" && "$device_code" == "$expected_product" ]] || fail 'Attached Android device is not E2003.'
[[ "$device_fingerprint" == 'Sony/E2003/E2003:4.4.4/25.0.A.2.31/4Pf_Nw:user/release-keys' ]] || fail 'Build fingerprint differs from the reviewed E2003 target.'
[[ "$customization" == '1293-7358' && "$custom_revision" == 'R7A' ]] || fail 'CDA/revision differs from the reviewed R7A target.'

printf '%s\n' 'Preflight passed for E2003 / 25.0.A.2.31 / 1293-7358 R7A.'
printf '%s\n' 'Entering Fastboot for identity checks; no partition will be written by those checks.'
"$adb_bin" -d reboot bootloader

fastboot_count=0
for attempt in $(seq 1 30); do
  fastboot_count=$("$fastboot_bin" devices | awk 'NF {n++} END {print n+0}')
  [[ "$fastboot_count" -gt 0 ]] && break
  sleep 1
done
[[ "$fastboot_count" == 1 ]] || fail 'Expected exactly one Fastboot target; unlock not attempted.'

product_result=$("$fastboot_bin" getvar product 2>&1 || true)
bootloader_result=$("$fastboot_bin" getvar version-bootloader 2>&1 || true)
unlocked_result=$("$fastboot_bin" getvar unlocked 2>&1 || true)
grep -q 'product: E2003' <<<"$product_result" || fail 'Fastboot product is not E2003; unlock not attempted.'
grep -Fq "$expected_bootloader" <<<"$bootloader_result" || fail 'Unexpected Fastboot bootloader; unlock not attempted.'
if grep -Eiq 'unlocked:[[:space:]]*(yes|true|1)' <<<"$unlocked_result"; then
  fail 'Fastboot already reports unlocked; no command sent.'
fi

printf '%s\n' 'Fastboot identity passed. Sending exactly one Sony bootloader-unlock command.'
printf '%s\n' 'The unlock code is not printed or saved; it is passed to Fastboot for this operation.'
if "$fastboot_bin" oem unlock "0x${unlock_code}"; then
  command_status=0
else
  command_status=$?
fi
unset unlock_code
if [[ "$command_status" -ne 0 ]]; then
  fail 'Fastboot unlock command failed. Do not retry automatically; inspect the device and output.'
fi

printf '%s\n' 'Fastboot accepted the unlock command. No flash, erase, or other partition command was issued.'
printf '%s\n' 'After Android starts, verify Service info > Configuration > Rooting Status says Bootloader unlocked: Yes.'
