#!/usr/bin/env python3
"""Read-only SHA-256 comparison of extracted Android /system directory trees.

Usage: compare_system_trees.py R7A_SYSTEM_ROOT R10A_SYSTEM_ROOT
The roots may be the extracted system directories themselves. Regular files and
file symlinks are hashed as file contents; symlinked directories are not walked.
No device access or writes are performed.
"""
from __future__ import annotations
import hashlib
import os
import sys
from pathlib import Path


def index(root: Path) -> dict[str, tuple[int, str]]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    result: dict[str, tuple[int, str]] = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(current) / d).is_symlink())
        for name in sorted(files):
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            if not path.is_file():
                continue
            h = hashlib.sha256()
            size = 0
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(block)
                    h.update(block)
            result[rel] = (size, h.hexdigest())
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {Path(sys.argv[0]).name} R7A_SYSTEM_ROOT R10A_SYSTEM_ROOT", file=sys.stderr)
        return 2
    try:
        left, right = index(Path(sys.argv[1])), index(Path(sys.argv[2]))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    common = left.keys() & right.keys()
    same = sum(left[p] == right[p] for p in common)
    size_diff = sum(left[p][0] != right[p][0] for p in common)
    content_diff = sum(left[p][1] != right[p][1] for p in common)
    content_only_diff = sum(left[p][0] == right[p][0] and left[p][1] != right[p][1] for p in common)
    print(f"left_files={len(left)}")
    print(f"right_files={len(right)}")
    print(f"common_paths={len(common)}")
    print(f"left_only={len(left.keys() - right.keys())}")
    print(f"right_only={len(right.keys() - left.keys())}")
    print(f"identical_size_and_hash={same}")
    print(f"size_mismatch={size_diff}")
    print(f"content_mismatch_including_size_differences={content_diff}")
    print(f"same_size_content_mismatch={content_only_diff}")
    print("DIFFERENCES (path<TAB>left_size<TAB>right_size<TAB>same_sha256)")
    for path in sorted(common):
        if left[path] != right[path]:
            print(f"{path}\t{left[path][0]}\t{right[path][0]}\t{left[path][1] == right[path][1]}")
    print("LEFT_ONLY")
    for path in sorted(left.keys() - right.keys()):
        print(path)
    print("RIGHT_ONLY")
    for path in sorted(right.keys() - left.keys()):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
