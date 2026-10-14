#!/usr/bin/env python3
"""Build an offline Android boot.img container POC from extracted E2003 data.

This does not create a verified or flashable boot image. It reuses only the
legacy header geometry from the retrieved E2003 TWRP reference and pairs it
with kernel/ramdisk payloads extracted from the unverified R10A stock FTF.
Output is restricted to a new path outside the Git repository. No device I/O.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import struct
import sys
from pathlib import Path

from verify_e2003_recovery import parse_newc, parse_recovery

ANDROID_MAGIC = b"ANDROID!"
MTK_MAGIC = bytes.fromhex("88168858")
PAGE_DEFAULT = 2048
MAX_SEGMENT = 64 * 1024 * 1024


def fail(message: str) -> None:
    raise ValueError(message)


def align(value: int, page_size: int) -> int:
    return (value + page_size - 1) // page_size * page_size


def load_mtk_rootfs(path: Path) -> tuple[bytes, list[str]]:
    data = path.read_bytes()
    if len(data) < 512 or data[:4] != MTK_MAGIC:
        fail("stock ramdisk is missing the expected MediaTek wrapper")
    payload_size = struct.unpack_from("<I", data, 4)[0]
    tag = data[8:40].split(b"\0", 1)[0]
    if tag != b"ROOTFS" or payload_size != len(data) - 512:
        fail("stock ramdisk wrapper tag/length is not the expected ROOTFS payload")
    cpio = gzip.decompress(data[512:])
    entries = parse_newc(cpio)
    required = {"init", "init.rc", "default.prop", "fstab"}
    missing = sorted(required - entries.keys())
    if missing:
        fail("stock ramdisk cpio is missing required files: " + ", ".join(missing))
    return data, sorted(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recovery_reference", type=Path,
                        help="local E2003 legacy Android recovery image used for header geometry")
    parser.add_argument("stock_kernel", type=Path,
                        help="raw E2003 kernel segment extracted from Sony ELF/SIN")
    parser.add_argument("stock_ramdisk", type=Path,
                        help="MediaTek ROOTFS-wrapped ramdisk segment extracted from Sony ELF/SIN")
    parser.add_argument("output", type=Path,
                        help="new absolute output path outside this Git repository")
    args = parser.parse_args()

    for label, path in (("recovery reference", args.recovery_reference),
                        ("stock kernel", args.stock_kernel),
                        ("stock ramdisk", args.stock_ramdisk)):
        if not path.is_file():
            fail(f"{label} is not a regular file")
    if not args.output.is_absolute() or args.output.exists():
        fail("output must be an absolute path that does not already exist")
    repo_root = Path(__file__).resolve().parents[3]
    if args.output.resolve().is_relative_to(repo_root):
        fail("refusing to place proprietary-derived boot image inside the repository")

    recovery_report, recovery_pass = parse_recovery(
        args.recovery_reference, args.stock_kernel, 32 * 1024 * 1024
    )
    if not recovery_pass or not recovery_report["identity_matches_e2003_kitkat"]:
        fail("recovery reference failed the existing E2003/API19 static checks")
    if recovery_report["page_size"] != PAGE_DEFAULT:
        fail("unsupported recovery header page size")

    kernel = args.stock_kernel.read_bytes()
    ramdisk, cpio_names = load_mtk_rootfs(args.stock_ramdisk)
    if len(kernel) > MAX_SEGMENT or len(ramdisk) > MAX_SEGMENT:
        fail("kernel or ramdisk exceeds the 64 MiB safety limit")
    if hashlib.sha256(kernel).hexdigest() != recovery_report["kernel_sha256"]:
        fail("stock kernel does not exactly match the E2003 recovery reference")

    reference = args.recovery_reference.read_bytes()
    page_size = recovery_report["page_size"]
    words = list(struct.unpack_from("<10I", reference, 8))
    if words[4] != 0 or words[8] != 0:
        fail("reference image has a second stage or DTB; this POC does not handle those")
    words[0] = len(kernel)
    words[2] = len(ramdisk)
    header = bytearray(reference[:page_size])
    struct.pack_into("<10I", header, 8, *words)
    header[48:64] = b"E2003-R10A-POC\0\0"

    # Android's legacy boot image ID is SHA-1 over each payload followed by its
    # little-endian length. The reference has no second stage in this format.
    image_id = hashlib.sha1(
        kernel + struct.pack("<I", len(kernel))
        + ramdisk + struct.pack("<I", len(ramdisk))
        + struct.pack("<I", 0)
    ).digest()
    header[576:608] = image_id + bytes(32 - len(image_id))

    image = bytearray(header)
    image.extend(kernel)
    image.extend(bytes(align(len(image), page_size) - len(image)))
    image.extend(ramdisk)
    image.extend(bytes(align(len(image), page_size) - len(image)))

    # Reparse the assembled legacy header and prove byte-for-byte segment roundtrip.
    if image[:8] != ANDROID_MAGIC:
        fail("internal error: Android boot magic was not preserved")
    check = struct.unpack_from("<10I", image, 8)
    check_kernel_size, check_ramdisk_size, check_page = check[0], check[2], check[7]
    if check_page != page_size or check_kernel_size != len(kernel) or check_ramdisk_size != len(ramdisk):
        fail("internal error: output header size fields disagree")
    kernel_start = page_size
    ramdisk_start = kernel_start + align(len(kernel), page_size)
    if bytes(image[kernel_start:kernel_start + len(kernel)]) != kernel:
        fail("internal error: kernel failed output roundtrip")
    if bytes(image[ramdisk_start:ramdisk_start + len(ramdisk)]) != ramdisk:
        fail("internal error: ramdisk failed output roundtrip")

    args.output.parent.mkdir(parents=False, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(image)

    print(f"output={args.output}")
    print(f"bytes={len(image)}")
    print(f"sha256={hashlib.sha256(image).hexdigest()}")
    print(f"kernel_sha256={hashlib.sha256(kernel).hexdigest()}")
    print(f"ramdisk_sha256={hashlib.sha256(ramdisk).hexdigest()}")
    print(f"header_page_size={page_size}")
    print(f"kernel_address=0x{words[1]:08x}")
    print(f"ramdisk_address=0x{words[3]:08x}")
    print(f"ramdisk_cpio_entries={len(cpio_names)}")
    print("status=OFFLINE_CONTAINER_POC_ONLY")
    print("warning=header geometry comes from an unaudited R5A recovery; payloads are unverified R10A stock data")
    print("warning=not boot-tested, not R7A-matched, not approved for flashing")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, struct.error, gzip.BadGzipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
