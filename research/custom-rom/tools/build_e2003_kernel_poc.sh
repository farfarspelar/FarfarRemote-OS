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
data_root=$(realpath -m -- "${FARFAR_DATA_ROOT:-/mnt/data/FarfarRemote-Research-POC}")
tmp_root=$(realpath -m -- "${FARFAR_TMPDIR:-"$data_root/tmp"}")
expected_commit=2a84825e8268393267e454e35a00f80d48c58949
expected_origin=https://gitlab.com/sobotkama/android_kernel_sony_e2003.git
compiler="$ndk_root/toolchains/arm-linux-androideabi-4.8/prebuilt/linux-x86_64/bin"

[[ -f "$source_tree/makeMtk" && -d "$source_tree/kernel" ]] || {
  echo "Not an E2003 kernel source tree: $source_tree" >&2
  exit 1
}

# Kernel outputs live inside the source tree; keep both them and tool temp off `/`.
root_fs=$(stat -f -c '%d' /)
source_fs=$(stat -f -c '%d' "$source_tree")
[[ "$source_fs" != "$root_fs" ]] || {
  echo "Kernel source/output tree is on the system filesystem; refusing to build: $source_tree" >&2
  exit 1
}
probe=$data_root
while [[ ! -e "$probe" ]]; do
  parent=$(dirname -- "$probe")
  [[ "$parent" != "$probe" ]] || { echo "Cannot find mounted data filesystem: $data_root" >&2; exit 1; }
  probe=$parent
done
data_fs=$(stat -f -c '%d' "$probe")
[[ "$source_fs" == "$data_fs" ]] || {
  echo "Kernel source/output tree must be on FARFAR_DATA_ROOT filesystem: $source_tree" >&2
  exit 1
}
tmp_probe=$tmp_root
while [[ ! -e "$tmp_probe" ]]; do
  parent=$(dirname -- "$tmp_probe")
  [[ "$parent" != "$tmp_probe" ]] || { echo "Cannot find data filesystem for temp path: $tmp_root" >&2; exit 1; }
  tmp_probe=$parent
done
tmp_fs=$(stat -f -c '%d' "$tmp_probe")
[[ "$tmp_fs" == "$data_fs" ]] || {
  echo "Kernel temporary path must be on FARFAR_DATA_ROOT filesystem: $tmp_root" >&2
  exit 1
}
free_bytes=$(df -PB1 "$source_tree" | awk 'END {print $4}')
(( free_bytes >= 5 * 1024 * 1024 * 1024 )) || {
  echo "At least 5 GiB must be free for the kernel build; currently ${free_bytes:-unknown} bytes: $source_tree" >&2
  exit 1
}
mkdir -p "$tmp_root"
export TMPDIR="$tmp_root" TEMP="$tmp_root" TMP="$tmp_root"

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
echo "Building pinned callass kernel source at $actual_commit"
echo "Build/output filesystem: $source_tree"
echo "Temporary directory: $TMPDIR"
echo "Python: $python_version"
echo "Compiler: $compiler/arm-linux-androideabi-gcc"
echo "This is an offline POC build and is not verified for flashing or booting."
cd "$source_tree"
PATH="$(dirname "$python2"):$compiler:$PATH" \
  HOST_EXTRACFLAGS=-fcommon \
  ./makeMtk callass n k
