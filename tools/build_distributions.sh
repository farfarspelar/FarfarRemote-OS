#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${AAPT:-}" ]]; then AAPT_BIN="$AAPT"; elif command -v aapt >/dev/null 2>&1; then AAPT_BIN="$(command -v aapt)"; else AAPT_BIN="$(find "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/nonexistent}}/build-tools" -name aapt -type f 2>/dev/null | sort -V | tail -n 1)"; fi
[[ -x "$AAPT_BIN" ]] || { echo "aapt not found; set ANDROID_HOME or AAPT" >&2; exit 1; }
cd "$ROOT_DIR"
python3 tools/test_v03_contract.py
./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug
mkdir -p dist
cp app/build/outputs/apk/app/debug/app-app-debug.apk dist/FarfarRemote-App-v0.4.0.apk
cp app/build/outputs/apk/os/debug/app-os-debug.apk dist/FarfarRemote-OS-v0.4.0.apk
"$AAPT_BIN" dump badging dist/FarfarRemote-App-v0.4.0.apk | grep -F "package: name='org.farfarremote.app' versionCode='4' versionName='0.4.0'" >/dev/null
"$AAPT_BIN" dump badging dist/FarfarRemote-OS-v0.4.0.apk | grep -F "package: name='org.farfarremote' versionCode='4' versionName='0.4.0'" >/dev/null
(cd dist && sha256sum FarfarRemote-App-v0.4.0.apk FarfarRemote-OS-v0.4.0.apk > SHA256SUMS-0.4.0.txt)
echo "Built and checked: dist/FarfarRemote-App-v0.4.0.apk and dist/FarfarRemote-OS-v0.4.0.apk"
cat dist/SHA256SUMS-0.4.0.txt
