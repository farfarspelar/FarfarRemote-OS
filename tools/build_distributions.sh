#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${AAPT:-}" ]]; then AAPT_BIN="$AAPT"; elif command -v aapt >/dev/null 2>&1; then AAPT_BIN="$(command -v aapt)"; else AAPT_BIN="$(find "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/nonexistent}}/build-tools" -name aapt -type f 2>/dev/null | sort -V | tail -n 1)"; fi
[[ -x "$AAPT_BIN" ]] || { echo "aapt not found; set ANDROID_HOME or AAPT" >&2; exit 1; }
cd "$ROOT_DIR"
python3 tools/test_v03_contract.py
./gradlew testAppDebugUnitTest testOsDebugUnitTest assembleAppDebug assembleOsDebug
mkdir -p dist
VERSION="0.4.7"
VERSION_CODE="15"
APP_APK="FarfarRemote-App-Android4.4plus-API19plus-v${VERSION}.apk"
OS_APK="FarfarRemote-OS-Android4.4plus-API19plus-v${VERSION}.apk"
cp app/build/outputs/apk/app/debug/app-app-debug.apk "dist/$APP_APK"
cp app/build/outputs/apk/os/debug/app-os-debug.apk "dist/$OS_APK"
"$AAPT_BIN" dump badging "dist/$APP_APK" | grep -F "package: name='org.farfarremote.app' versionCode='${VERSION_CODE}' versionName='${VERSION}'" >/dev/null
"$AAPT_BIN" dump badging "dist/$OS_APK" | grep -F "package: name='org.farfarremote' versionCode='${VERSION_CODE}' versionName='${VERSION}'" >/dev/null
"$AAPT_BIN" dump badging "dist/$APP_APK" | grep -F "sdkVersion:'19'" >/dev/null
"$AAPT_BIN" dump badging "dist/$OS_APK" | grep -F "sdkVersion:'19'" >/dev/null
"$AAPT_BIN" dump badging "dist/$APP_APK" | grep -F "targetSdkVersion:'36'" >/dev/null
"$AAPT_BIN" dump badging "dist/$OS_APK" | grep -F "targetSdkVersion:'28'" >/dev/null
(cd dist && sha256sum "$APP_APK" > "$APP_APK.sha256" && sha256sum "$OS_APK" > "$OS_APK.sha256" && sha256sum "$APP_APK" "$OS_APK" > "SHA256SUMS-${VERSION}.txt")
echo "Built and checked: dist/$APP_APK and dist/$OS_APK"
cat "dist/SHA256SUMS-${VERSION}.txt"
