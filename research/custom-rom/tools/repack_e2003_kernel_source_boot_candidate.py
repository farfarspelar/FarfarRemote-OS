#!/usr/bin/env python3
"""Assemble an offline E2003 boot-image container using the callass zImage.

This is an experimental container only. Header geometry comes from an
unaudited E2003 R5A recovery; the rootfs comes from a community R10A firmware
candidate. It is not R7A-matched, boot-tested, signed, or flash-approved.
No device I/O is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

from repack_e2003_stock_boot_poc import (
    ANDROID_MAGIC, MAX_SEGMENT, PAGE_DEFAULT, align, load_mtk_rootfs,
)
from verify_e2003_recovery import parse_recovery

ZIMAGE_MAGIC = b"\x18\x28\x6f\x01"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recovery_reference", type=Path,
                        help="local E2003 recovery image supplying legacy header geometry")
    parser.add_argument("stock_kernel_reference", type=Path,
                        help="extracted E2003 stock kernel used to validate the recovery reference")
    parser.add_argument("candidate_zimage", type=Path,
                        help="offline ARM zImage built from the pinned callass kernel source")
    parser.add_argument("stock_ramdisk", type=Path,
                        help="MediaTek ROOTFS-wrapped ramdisk from the local R10A candidate")
    parser.add_argument("output", type=Path,
                        help="new absolute output path outside the Git repository")
    args = parser.parse_args()

    for label, path in (("recovery reference", args.recovery_reference),
                        ("stock kernel reference", args.stock_kernel_reference),
                        ("candidate zImage", args.candidate_zimage),
                        ("stock ramdisk", args.stock_ramdisk)):
        if not path.is_file():
            parser.error(f"{label} is not a regular file: {path}")
    if not args.output.is_absolute() or args.output.exists():
        parser.error("output must be a new absolute path")
    repo_root = Path(__file__).resolve().parents[3]
    if args.output.resolve().is_relative_to(repo_root):
        parser.error("refusing to place proprietary-derived boot candidate in the repository")

    report, recovery_ok = parse_recovery(
        args.recovery_reference, args.stock_kernel_reference, 32 * 1024 * 1024
    )
    if not recovery_ok or not report["identity_matches_e2003_kitkat"]:
        parser.error("recovery reference failed existing E2003/API19 static checks")
    if report["page_size"] != PAGE_DEFAULT:
        parser.error("unsupported recovery header page size")

    kernel = args.candidate_zimage.read_bytes()
    if len(kernel) <= 0x28 or kernel[0x24:0x28] != ZIMAGE_MAGIC:
        parser.error("candidate does not contain the expected ARM zImage magic")
    ramdisk, entries = load_mtk_rootfs(args.stock_ramdisk)
    if len(kernel) > MAX_SEGMENT or len(ramdisk) > MAX_SEGMENT:
        parser.error("kernel or ramdisk exceeds the 64 MiB static-PoC bound")

    reference = args.recovery_reference.read_bytes()
    words = list(struct.unpack_from("<10I", reference, 8))
    if words[4] != 0 or words[8] != 0:
        parser.error("reference has a second stage or DTB; unsupported by this container builder")
    words[0] = len(kernel)
    words[2] = len(ramdisk)
    header = bytearray(reference[:PAGE_DEFAULT])
    struct.pack_into("<10I", header, 8, *words)
    header[48:64] = b"E2003-KSRC-POC\0\0"
    image_id = hashlib.sha1(
        kernel + struct.pack("<I", len(kernel))
        + ramdisk + struct.pack("<I", len(ramdisk))
        + struct.pack("<I", 0)
    ).digest()
    header[576:608] = image_id + bytes(32 - len(image_id))

    image = bytearray(header)
    image.extend(kernel)
    image.extend(bytes(align(len(image), PAGE_DEFAULT) - len(image)))
    ramdisk_start = len(image)
    image.extend(ramdisk)
    image.extend(bytes(align(len(image), PAGE_DEFAULT) - len(image)))

    if image[:8] != ANDROID_MAGIC:
        raise ValueError("internal error: output lost Android boot magic")
    readback = struct.unpack_from("<10I", image, 8)
    kernel_start = PAGE_DEFAULT
    if image[kernel_start:kernel_start + len(kernel)] != kernel:
        raise ValueError("internal error: kernel segment readback failed")
    if image[ramdisk_start:ramdisk_start + len(ramdisk)] != ramdisk:
        raise ValueError("internal error: ramdisk segment readback failed")
    if readback[0] != len(kernel) or readback[2] != len(ramdisk):
        raise ValueError("internal error: boot header segment lengths disagree")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(image)
    print("output_bytes:", len(image))
    print("output_sha256:", hashlib.sha256(image).hexdigest())
    print("kernel_bytes:", len(kernel))
    print("kernel_sha256:", hashlib.sha256(kernel).hexdigest())
    print("ramdisk_bytes:", len(ramdisk))
    print("ramdisk_sha256:", hashlib.sha256(ramdisk).hexdigest())
    print("ramdisk_cpio_entries:", len(entries))
    print("status=OFFLINE_CONTAINER_POC_ONLY")
    print("warning=header from unaudited E2003 R5A recovery; rootfs from community E2003 R10A candidate")
    print("warning=kernel source config is not verified against live R7A; not boot-tested or flashable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
