#!/usr/bin/env bash
set -euo pipefail

# Offline-only proof of concept: add the already-built OS APK to an exact,
# locally supplied copy of the inspected E2003 R10A system.ext4 image.
# This does not create a flashable Sony SIN/FTF or touch any connected device.

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <R10A-system.ext4> <FarfarRemote-OS.apk> <output-system.ext4>" >&2
  exit 2
fi

src=$(realpath -- "$1")
apk=$(realpath -- "$2")
out=$(realpath -m -- "$3")
repo_root=$(git rev-parse --show-toplevel)

for tool in debugfs e2fsck sha256sum keytool jarsigner file cmp; do
  command -v "$tool" >/dev/null || { echo "Required tool missing: $tool" >&2; exit 2; }
done
[[ -n "${AAPT2_BIN:-}" ]] || { echo "Set AAPT2_BIN to Android SDK aapt2." >&2; exit 2; }
[[ -x "$AAPT2_BIN" ]] || { echo "AAPT2_BIN is not executable: $AAPT2_BIN" >&2; exit 2; }
[[ -f "$src" && -f "$apk" ]] || { echo "Input file not found." >&2; exit 2; }
[[ "$out" != "$src" && "$out" != "$apk" ]] || { echo "Output must differ from both inputs." >&2; exit 2; }
case "$out" in "$repo_root"/*) echo "Refusing to write firmware artifacts inside the Git repository." >&2; exit 2;; esac
[[ ! -e "$out" ]] || { echo "Refusing to overwrite existing output: $out" >&2; exit 2; }

expected_system_sha=931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949
actual_system_sha=$(sha256sum "$src" | cut -d ' ' -f1)
[[ "$actual_system_sha" == "$expected_system_sha" ]] || {
  echo "Input system image hash mismatch; expected the inspected R10A image." >&2
  exit 1
}

badging=$("$AAPT2_BIN" dump badging "$apk")
grep -Fq "package: name='org.farfarremote'" <<<"$badging" || { echo "APK is not the FarfarRemote OS package." >&2; exit 1; }
grep -Fq "minSdkVersion:'19'" <<<"$badging" || { echo "APK minSdkVersion is not 19." >&2; exit 1; }
cert=$(keytool -printcert -jarfile "$apk" 2>/dev/null | awk -F': ' '/SHA256:/{gsub(":", "", $2); print toupper($2); exit}')
[[ "$cert" == "63F9336D0038B8EBE9AC8224F8869E1F871828D81B6269372315CE055CF607FD" ]] || {
  echo "APK signing certificate does not match the E2003 installed OS APK." >&2
  exit 1
}
jarsigner -verify "$apk" >/dev/null 2>&1 || { echo "APK v1 signature verification failed." >&2; exit 1; }

mkdir -p "$(dirname -- "$out")"
stage=$(mktemp -d /tmp/farfar-system-poc.XXXXXX)
tmp_out="${out}.tmp.$$"
cleanup() { rm -rf -- "$stage"; rm -f -- "$tmp_out"; }
trap cleanup EXIT
cp -- "$apk" "$stage/FarfarRemote.apk"
cp --sparse=always -- "$src" "$tmp_out"

debugfs -w -R "write $stage/FarfarRemote.apk /app/FarfarRemote.apk" "$tmp_out" >/dev/null
debugfs -w -R 'sif /app/FarfarRemote.apk uid 0' "$tmp_out" >/dev/null
debugfs -w -R 'sif /app/FarfarRemote.apk gid 0' "$tmp_out" >/dev/null
debugfs -w -R 'sif /app/FarfarRemote.apk mode 0100644' "$tmp_out" >/dev/null
debugfs -w -R 'ea_set /app/FarfarRemote.apk security.selinux u:object_r:system_file:s0' "$tmp_out" >/dev/null

debugfs -R "dump /app/FarfarRemote.apk $stage/readback.apk" "$tmp_out" >/dev/null
cmp -- "$stage/FarfarRemote.apk" "$stage/readback.apk"
debugfs -R 'stat /app/FarfarRemote.apk' "$tmp_out" 2>/dev/null | grep -Fq 'Mode:  0644'
debugfs -R 'ea_list /app/FarfarRemote.apk' "$tmp_out" 2>/dev/null | grep -Fq 'u:object_r:system_file:s0'
file "$tmp_out" | grep -Fq 'ext4 filesystem data'

set +e
e2fsck -fn "$tmp_out" >"$stage/e2fsck.txt" 2>&1
fsck_status=$?
set -e
if [[ $fsck_status -ne 0 && $fsck_status -ne 4 ]]; then
  cat "$stage/e2fsck.txt" >&2
  echo "Filesystem check returned unexpected status $fsck_status." >&2
  exit 1
fi

mv -- "$tmp_out" "$out"
trap - EXIT
rm -rf -- "$stage"
printf 'Offline system-image POC: %s\n' "$out"
printf 'SHA-256: %s\n' "$(sha256sum "$out" | cut -d ' ' -f1)"
printf 'APK SHA-256: %s\n' "$(sha256sum "$apk" | cut -d ' ' -f1)"
printf 'e2fsck exit: %s (status 4 is the previously documented inode-bitmap padding warning if reported)\n' "$fsck_status"
echo 'This is not a flashable firmware package and has not been booted.'
