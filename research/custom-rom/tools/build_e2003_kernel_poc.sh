#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: build_e2003_kernel_poc.sh SOURCE_TREE NDK_ROOT PYTHON2

Builds the pinned E2003/callass kernel source mirror locally. This only creates
host-side build outputs; it does not use ADB/Fastboot or install anything.

Expected source commit: 2a84825e8268393267e454e35a00f80d48c58949
Expected toolchain: Android NDK r10e arm-linux-androideabi GCC 4.8
EOF
  exit 2
}

[[ $# -eq 3 ]] || usage
source_tree=$(realpath "$1")
ndk_root=$(realpath "$2")
python2=$(realpath "$3")
expected_commit=2a84825e8268393267e454e35a00f80d48c58949
expected_origin=https://gitlab.com/sobotkama/android_kernel_sony_e2003.git
compiler="$ndk_root/toolchains/arm-linux-androideabi-4.8/prebuilt/linux-x86_64/bin"

[[ -f "$source_tree/makeMtk" && -d "$source_tree/kernel" ]] || {
  echo "Not an E2003 kernel source tree: $source_tree" >&2
  exit 1
}
actual_commit=$(git -C "$source_tree" rev-parse HEAD)
[[ "$actual_commit" == "$expected_commit" ]] || {
  echo "Refusing unpinned source commit: $actual_commit" >&2
  exit 1
}
actual_origin=$(git -C "$source_tree" remote get-url origin)
[[ "${actual_origin%.git}" == "${expected_origin%.git}" ]] || {
  echo "Refusing unexpected source origin: $actual_origin" >&2
  exit 1
}
[[ -x "$compiler/arm-linux-androideabi-gcc" ]] || {
  echo "NDK r10e GCC 4.8 compiler not found under: $ndk_root" >&2
  exit 1
}
[[ -x "$python2" ]] || {
  echo "Python 2 executable not found: $python2" >&2
  exit 1
}
python_version=$("$python2" --version 2>&1)
[[ "$python_version" == "Python 2.7."* ]] || {
  echo "Expected Python 2.7, got: $python_version" >&2
  exit 1
}
available_kb=$(df -Pk "$source_tree" | awk 'NR == 2 {print $4}')
[[ "$available_kb" =~ ^[0-9]+$ ]] && (( available_kb >= 3145728 )) || {
  echo "At least 3 GiB free space is required at $source_tree" >&2
  exit 1
}

echo "Building pinned callass kernel source at $actual_commit"
echo "Python: $python_version"
echo "Compiler: $compiler/arm-linux-androideabi-gcc"
echo "This is an offline POC build and is not verified for flashing or booting."
cd "$source_tree"
PATH="$(dirname "$python2"):$compiler:$PATH" \
  HOST_EXTRACFLAGS=-fcommon \
  ./makeMtk callass n k
