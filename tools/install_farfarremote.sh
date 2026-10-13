#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADB_BIN="${ADB:-adb}"
APK="${1:-$ROOT_DIR/dist/FarfarRemote-OS-v0.4.2-rc1.apk}"
if [[ -n "${AAPT:-}" ]]; then AAPT_BIN="$AAPT"; elif command -v aapt >/dev/null 2>&1; then AAPT_BIN="$(command -v aapt)"; else AAPT_BIN="$(find "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/nonexistent}}/build-tools" -name aapt -type f 2>/dev/null | sort -V | tail -n 1)"; fi
command -v "$ADB_BIN" >/dev/null 2>&1 || { echo "adb not found" >&2; exit 1; }
[[ -f "$APK" ]] || { echo "APK missing; build first: ./gradlew assembleDebug" >&2; exit 1; }
[[ -x "$AAPT_BIN" ]] || { echo "aapt not found; set ANDROID_HOME or AAPT" >&2; exit 1; }
"$AAPT_BIN" dump badging "$APK" | grep -F "package: name='org.farfarremote'" >/dev/null || { echo "refusing install: this installer accepts only the OS package org.farfarremote" >&2; exit 1; }
mapfile -t ONLINE < <("$ADB_BIN" devices | awk 'NR > 1 && $2 == "device" {print $1}')
((${#ONLINE[@]} == 1)) || { echo "expected exactly one authorized adb device" >&2; exit 1; }
SERIAL="${ONLINE[0]}"
MODEL="$("$ADB_BIN" -s "$SERIAL" shell getprop ro.product.model | tr -d '\r')"
DEVICE="$("$ADB_BIN" -s "$SERIAL" shell getprop ro.product.device | tr -d '\r')"
PRODUCT="$("$ADB_BIN" -s "$SERIAL" shell getprop ro.build.product | tr -d '\r')"
if [[ "$MODEL" != *E2003* && "$DEVICE" != *E2003* && "$PRODUCT" != *E2003* ]]; then
  echo "refusing install: identity mismatch model='$MODEL' device='$DEVICE' product='$PRODUCT'" >&2; exit 1
fi
echo "Target: $SERIAL ($MODEL / $DEVICE / $PRODUCT)"
echo "Installing OS flavor only (package org.farfarremote). Existing app data will be retained by adb install -r."
"$ADB_BIN" -s "$SERIAL" install -r "$APK"
"$ADB_BIN" -s "$SERIAL" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
