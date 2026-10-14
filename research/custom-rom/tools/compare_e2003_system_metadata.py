#!/usr/bin/env python3
"""Compare live E2003 /system metadata with a local ext4 system image.

The live metadata file is produced by capture_e2003_system_metadata.sh and
must remain outside Git. This tool invokes debugfs read-only; it never mounts
or modifies the image or communicates with a device.
"""
from __future__ import annotations

import hashlib
import argparse
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

EXPECTED_IMAGE_SHA256 = "931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949"
ENTRY = re.compile(r"^([bcdlps-][rwxStTs-]{9})\s+(\S+)\s+(\S+)\s+(u:object_r:[^\s]+)\s+(.*)$")
PROMPT = re.compile(r"^debugfs: stat (.*)$")
UID = {"root": 0, "shell": 2000, "dhcp": 1014}
GID = {"root": 0, "shell": 2000, "system": 1000, "inet": 3003}
TYPE = {"regular": "-", "directory": "d", "symlink": "l", "character": "c", "block": "b", "fifo": "p", "socket": "s"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mode_bits(text: str) -> int:
    bits = (0o400, 0o200, 0o100, 0o040, 0o020, 0o010, 0o004, 0o002, 0o001)
    value = 0
    for char, bit in zip(text[1:], bits):
        if char in "rwxst" or (char in "sS" and bit in (0o100, 0o010)) or (char in "tT" and bit == 0o001):
            value |= bit
    if text[3] in "sS":
        value |= 0o4000
    if text[6] in "sS":
        value |= 0o2000
    if text[9] in "tT":
        value |= 0o1000
    return value


def read_live(path: Path) -> dict[str, tuple[str, int, object, object, str, str]]:
    headers: dict[str, str] = {}
    result = {}
    current = None
    for raw in path.read_text(errors="replace").splitlines():
        if raw.startswith("# target_") and "=" in raw:
            key, value = raw[2:].split("=", 1)
            headers[key] = value
            continue
        if raw.startswith("/") and raw.endswith(":"):
            current = raw[:-1]
            continue
        match = ENTRY.match(raw)
        if not match or current is None:
            continue
        perm, owner, group, label, name = match.groups()
        if name in (".", ".."):
            continue
        target = ""
        if perm[0] == "l" and " -> " in name:
            name, target = name.split(" -> ", 1)
        rel = (current + "/" + name).removeprefix("/system")
        if any(char.isspace() for char in rel):
            raise ValueError(f"Whitespace in path cannot be represented safely: {rel!r}")
        result[rel] = (perm[0], mode_bits(perm), UID.get(owner, owner), GID.get(group, group), label, target)
    expected = {
        "target_model": "E2003",
        "target_build": "25.0.A.2.31",
        "target_cda": "1293-7358",
        "target_revision": "R7A",
    }
    for key, value in expected.items():
        if headers.get(key) != value:
            raise ValueError(f"Metadata header {key} must be {value!r}; got {headers.get(key)!r}")
    if not result:
        raise ValueError("No /system entries parsed from metadata file")
    return result


def read_candidate(image: Path, paths: list[str]) -> tuple[dict[str, tuple[str, int, int, int, str, str]], set[str]]:
    stats = {}
    missing = set()
    current = None
    block: list[str] = []

    def save() -> None:
        if current is None:
            return
        joined = "\n".join(block)
        if "File not found" in joined or "File not found by ext2_lookup" in joined:
            missing.add(current)
            return
        first = re.search(r"Inode:.*?Type: (\w+).*?Mode:\s+(\d+)", joined)
        owner = re.search(r"User:\s*(\d+)\s+Group:\s*(\d+)", joined)
        label = re.search(r'security\.selinux \(\d+\) = "([^"\\]+)', joined)
        link = re.search(r'Fast link dest: "([^"]*)"', joined)
        if not first or not owner:
            missing.add(current)
            return
        stats[current] = (
            TYPE.get(first.group(1), "?"),
            int(first.group(2), 8),
            int(owner.group(1)),
            int(owner.group(2)),
            label.group(1) if label else "",
            link.group(1) if link else "",
        )

    # Run once more with captured output outside the temporary-command context.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="e2003-stat-") as commands:
        commands.write("".join(f"stat {path}\n" for path in paths))
        commands.flush()
        proc = subprocess.run(["debugfs", "-f", commands.name, str(image)], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"debugfs failed (exit {proc.returncode}): {proc.stderr.strip()}")
    for raw in proc.stdout.splitlines():
        match = PROMPT.match(raw)
        if match:
            save()
            current = match.group(1)
            block = []
        elif current is not None:
            block.append(raw)
    save()
    # `debugfs stat` omits the value for some longer xattrs even though the
    # attribute is present. Query those labels directly to avoid a false
    # mismatch in the metadata audit.
    for path, value in list(stats.items()):
        if value[4]:
            continue
        check = subprocess.run(["debugfs", "-R", f"ea_get {path} security.selinux", str(image)],
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        match = re.search(r'security\.selinux \(\d+\) = "([^"\\]*)"', check.stdout + check.stderr)
        if match:
            stats[path] = (*value[:4], match.group(1), value[5])
    return stats, missing


def compare_payloads(image: Path, live: dict, live_root: Path) -> tuple[int, int, list[str]]:
    regular = sorted(path for path, entry in live.items() if entry[0] == "-")
    mismatches: list[str] = []
    with tempfile.TemporaryDirectory(prefix="e2003-content-check-") as temp_name:
        work = Path(temp_name)
        command_file = work / "dump.commands"
        dumps: dict[str, Path] = {}
        lines = []
        for index, path in enumerate(regular):
            source_file = live_root / path.lstrip("/")
            if not source_file.is_file():
                raise ValueError(f"Captured live file is missing: {source_file}")
            destination = work / f"payload-{index:04d}"
            dumps[path] = destination
            lines.append(f"dump {path} {destination}")
        command_file.write_text("\n".join(lines) + "\n")
        proc = subprocess.run(["debugfs", "-f", str(command_file), str(image)], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"debugfs payload dump failed (exit {proc.returncode})")
        for path, dump_path in dumps.items():
            source_file = live_root / path.lstrip("/")
            if not dump_path.is_file() or sha256(dump_path) != sha256(source_file):
                mismatches.append(path)
    return len(regular) - len(mismatches), len(regular), mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-unpinned-candidate", action="store_true",
                        help="permit a local POC image in place of the pinned R10A source image")
    parser.add_argument("--compare-payloads", metavar="R7A_SYSTEM_ROOT",
                        help="also hash every regular file against the private ADB-pulled R7A tree")
    parser.add_argument("metadata", type=Path)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    metadata, image = args.metadata, args.image
    try:
        if not metadata.is_file() or not image.is_file():
            raise ValueError("metadata and image inputs must be files")
        actual_hash = sha256(image)
        if not args.allow_unpinned_candidate and actual_hash != EXPECTED_IMAGE_SHA256:
            raise ValueError("system image hash does not match the inspected R10A candidate")
        live = read_live(metadata)
        candidate, missing = read_candidate(image, sorted(live))
    except (OSError, ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    common = set(live) & set(candidate)
    print(f"candidate_sha256={actual_hash}")
    if args.allow_unpinned_candidate:
        print("candidate_hash_status=UNPINNED_LOCAL_POC")
    print(f"live_manifest_entries={len(live)}")
    print(f"candidate_entries_checked={len(candidate)}")
    print(f"live_paths_absent_from_candidate={len(set(live) - set(candidate))}")
    print(f"candidate_paths_not_checked={len(missing)}")
    for index, field in enumerate(("type", "mode", "uid", "gid", "selinux", "symlink_target")):
        mismatches = sorted(path for path in common if live[path][index] != candidate[path][index])
        print(f"{field}_matches={len(common) - len(mismatches)}")
        print(f"{field}_mismatches={len(mismatches)}")
        for path in mismatches:
            print(f"  {field}: {path}: live={live[path][index]!r} candidate={candidate[path][index]!r}")
    if missing:
        print("candidate_stat_errors=" + ",".join(sorted(missing)[:20]))
    if args.compare_payloads:
        matched, total, payload_mismatches = compare_payloads(image, live, Path(args.compare_payloads))
        print(f"regular_file_payloads_matching={matched}")
        print(f"regular_file_payloads_checked={total}")
        for path in payload_mismatches[:20]:
            print(f"  payload_mismatch: {path}")
        if payload_mismatches:
            return 1
    if missing or set(live) - set(candidate):
        return 1
    if any(live[path][index] != candidate[path][index]
           for path in common for index in range(6)):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
