#!/usr/bin/env bash
# Read-only inventory of the local ROM research/build host.
set -euo pipefail

printf 'Host: '; uname -srm
printf '\nCPU threads: '; nproc 2>/dev/null || getconf _NPROCESSORS_ONLN
printf '\nMemory:\n'; free -h 2>/dev/null || awk '/MemTotal|MemAvailable/ {print}' /proc/meminfo
printf '\nBuild/storage target filesystems (workspace and /tmp):\n'; df -h . /tmp
printf '\nTool availability:\n'
for tool in git python3 java adb fastboot unzip zipinfo sha256sum file repo ndk-build emulator lunch; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '  %-12s %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '  %-12s missing\n' "$tool"
  fi
done
if command -v java >/dev/null 2>&1; then
  java -version 2>&1 | head -n 3
fi
printf '\nThis script does not query, reboot, or modify an Android device.\n'
