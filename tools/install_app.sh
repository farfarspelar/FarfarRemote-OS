#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADB_BIN="${ADB:-adb}"
APK="${1:-$ROOT_DIR/dist/FarfarRemote-App-v0.4.2-rc1.apk}"
if [[ -n "${AAPT:-}" ]]; then AAPT_BIN="$AAPT"; elif command -v aapt >/dev/null 2>&1; then AAPT_BIN="$(command -v aapt)"; else AAPT_BIN="$(find "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/nonexistent}}/build-tools" -name aapt -type f 2>/dev/null | sort -V | tail -n 1)"; fi
command -v "$ADB_BIN" >/dev/null 2>&1 || { echo "adb not found" >&2; exit 1; }
[[ -x "$AAPT_BIN" ]] || { echo "aapt not found; set ANDROID_HOME or AAPT" >&2; exit 1; }
[[ -f "$APK" ]] || { echo "App APK missing; run ./tools/build_distributions.sh" >&2; exit 1; }
"$AAPT_BIN" dump badging "$APK" | grep -F "package: name='org.farfarremote.app'" >/dev/null || { echo "refusing install: expected App flavor package org.farfarremote.app" >&2; exit 1; }
mapfile -t ONLINE < <("$ADB_BIN" devices | awk 'NR > 1 && $2 == "device" {print $1}')
((${#ONLINE[@]} == 1)) || { echo "expected exactly one authorized adb device" >&2; exit 1; }
SERIAL="${ONLINE[0]}"
echo "Installing normal App flavor as separate package org.farfarremote.app on $SERIAL. The OS flavor uses org.farfarremote and is not replaced."
"$ADB_BIN" -s "$SERIAL" install -r "$APK"
"$ADB_BIN" -s "$SERIAL" shell am start -n org.farfarremote.app/org.farfarremote.MainActivity
