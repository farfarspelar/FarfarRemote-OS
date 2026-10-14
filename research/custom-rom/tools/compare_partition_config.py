#!/usr/bin/env python3
"""Compare candidate MTK BoardConfig partition sizes to a read-only ADB capture.

This is an offline consistency check only. It does not contact Android/Fastboot,
and a match is not evidence that the candidate firmware is authentic or safe to
flash. Inputs are the stdout capture from collect_e2003_prerequisites.sh and
one or more candidate Android BoardConfig/partition_size makefiles.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PARTITION_LINE = re.compile(
    r"^\s*\d+\s+\d+\s+(\d+)\s+(mmcblk0p\d+)\s*$", re.MULTILINE
)
ALIAS_LINE = re.compile(
    r"\b([A-Za-z0-9_]+)\s+->\s+/dev/block/(mmcblk0p\d+)\b"
)
SIZE_LINE = re.compile(
    r"^\s*(BOARD_([A-Z0-9_]+)IMAGE_PARTITION_SIZE)\s*:?=\s*"
    r"(0[xX][0-9a-fA-F]+|[0-9]+)\s*(?:#.*)?$",
    re.MULTILINE,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("live_capture", type=Path, help="stdout from collect_e2003_prerequisites.sh")
    parser.add_argument(
        "candidate_makefiles",
        type=Path,
        nargs="+",
        help="candidate BoardConfig.mk / partition_size.mk files",
    )
    args = parser.parse_args()

    try:
        live = read_text(args.live_capture)
        configs = "\n".join(read_text(path) for path in args.candidate_makefiles)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if "--- Memory and partition metadata (no partition contents) ---" not in live:
        print("ERROR: live capture lacks the expected partition metadata section", file=sys.stderr)
        return 2
    memory_section = live.split(
        "--- Memory and partition metadata (no partition contents) ---", 1
    )[1].split("--- Kernel module", 1)[0]

    partition_bytes = {
        name: int(kib) * 1024 for kib, name in PARTITION_LINE.findall(memory_section)
    }
    aliases = dict(ALIAS_LINE.findall(memory_section))
    sizes = SIZE_LINE.findall(configs)
    if not partition_bytes or not aliases:
        print("ERROR: no mmcblk0 partition table or by-name aliases found", file=sys.stderr)
        return 2
    if not sizes:
        print("ERROR: no BOARD_*IMAGE_PARTITION_SIZE values found", file=sys.stderr)
        return 2

    print("Candidate BoardConfig size versus live E2003 partition metadata")
    print("Status is a size comparison only; it does not validate image compatibility or restore safety.")
    print(f"{'Variable':43} {'Candidate':>14} {'Live':>14} {'Alias':>13}  Result")
    mismatches = 0
    unverified = 0
    for variable, suffix, raw_size in sizes:
        alias_name = suffix.lower()
        block = aliases.get(alias_name)
        actual = partition_bytes.get(block) if block else None
        candidate = int(raw_size, 0)
        if actual is None:
            result = "UNVERIFIED"
            live_text = "unknown"
            block_text = block or "unmapped"
            unverified += 1
        elif actual == candidate:
            result = "MATCH"
            live_text = str(actual)
            block_text = block
        else:
            result = "MISMATCH"
            live_text = str(actual)
            block_text = block
            mismatches += 1
        print(f"{variable:43} {candidate:>14} {live_text:>14} {block_text:>13}  {result}")

    for alias_name in ("boot", "fotakernel"):
        block = aliases.get(alias_name)
        actual = partition_bytes.get(block) if block else None
        print(
            f"LIVE_{alias_name.upper():37} {'not in candidate':>14} "
            f"{actual if actual is not None else 'unknown':>14} {block or 'unmapped':>13}  OBSERVED"
        )

    print(f"Summary: {len(sizes)} candidate size(s), {mismatches} mismatch(es), {unverified} unverified.")
    if mismatches:
        return 1
    if unverified:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
