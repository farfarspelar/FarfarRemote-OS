#!/usr/bin/env python3
"""Statically inspect a legacy Android recovery image for Xperia E2003.

This tool only reads local files. It never accesses ADB/Fastboot or writes an
image. A matching kernel and fitting image are static clues, not a boot test.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import struct
import sys
from pathlib import Path

PAGE_DEFAULT = 2048
MTK_MAGIC = bytes.fromhex("88168858")
BOOT_MAGIC = b"ANDROID!"
EXPECTED_BUILD = "25.0.A.2.31"
EXPECTED_MODEL = "E2003"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align(value: int, page: int) -> int:
    return (value + page - 1) // page * page


def parse_newc(data: bytes) -> dict[str, bytes]:
    """Return regular-file contents from a cpio newc archive; do not extract."""
    entries: dict[str, bytes] = {}
    pos = 0
    while pos + 110 <= len(data):
        header = data[pos:pos + 110]
        if header[:6] not in (b"070701", b"070702"):
            raise ValueError(f"invalid cpio newc header at offset {pos}")
        fields = [int(header[6 + i * 8:14 + i * 8], 16) for i in range(13)]
        mode, size, namesize = fields[1], fields[6], fields[11]
        pos += 110
        if namesize < 1 or pos + namesize > len(data):
            raise ValueError("invalid cpio name length")
        raw_name = data[pos:pos + namesize]
        if not raw_name.endswith(b"\0"):
            raise ValueError("unterminated cpio name")
        name = raw_name[:-1].decode("utf-8", "replace").lstrip("./")
        pos = align(pos + namesize, 4)
        if size > len(data) - pos:
            raise ValueError(f"invalid cpio file length for {name!r}")
        payload = data[pos:pos + size]
        pos = align(pos + size, 4)
        if name == "TRAILER!!!":
            return entries
        if mode & 0o170000 == 0o100000:
            entries[name] = payload
    raise ValueError("cpio archive has no TRAILER!!! entry")


def parse_recovery(path: Path, stock_kernel_path: Path, partition_bytes: int) -> tuple[dict, bool]:
    image = path.read_bytes()
    if len(image) < PAGE_DEFAULT or image[:8] != BOOT_MAGIC:
        raise ValueError("not a legacy Android boot image (ANDROID! header missing)")
    words = struct.unpack_from("<10I", image, 8)
    kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, dt_size, _ = words
    if page_size < 512 or page_size > 65536 or page_size & (page_size - 1):
        raise ValueError(f"invalid boot page size {page_size}")
    name = image[48:64].split(b"\0", 1)[0].decode("ascii", "replace")
    cmdline = image[64:64 + 512].split(b"\0", 1)[0].decode("ascii", "replace")
    kernel_start = page_size
    ramdisk_start = kernel_start + align(kernel_size, page_size)
    ramdisk_end = ramdisk_start + ramdisk_size
    if kernel_size == 0 or ramdisk_size == 0 or ramdisk_end > len(image):
        raise ValueError("boot image segment sizes exceed the file")
    kernel = image[kernel_start:kernel_start + kernel_size]
    ramdisk = image[ramdisk_start:ramdisk_end]
    stock_kernel = stock_kernel_path.read_bytes()
    kernel_match = sha256(kernel) == sha256(stock_kernel)

    compressed = ramdisk
    mtk_tag = "absent"
    if ramdisk.startswith(MTK_MAGIC):
        if len(ramdisk) < 512:
            raise ValueError("truncated MediaTek ramdisk wrapper")
        declared = struct.unpack_from("<I", ramdisk, 4)[0]
        mtk_tag = ramdisk[8:40].split(b"\0", 1)[0].decode("ascii", "replace")
        compressed = ramdisk[512:]
        if declared != len(ramdisk) - 512:
            raise ValueError("MediaTek wrapper payload length disagrees with ramdisk segment")
    cpio = gzip.decompress(compressed)
    entries = parse_newc(cpio)
    props = entries.get("default.prop", b"").decode("utf-8", "replace")
    fstab = entries.get("etc/recovery.fstab", b"").decode("utf-8", "replace")
    propmap = {}
    for line in props.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            propmap[key.strip()] = value.strip()
    recovery_rows = [line.strip() for line in fstab.splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
    recovery_row = next((row for row in recovery_rows if row.split()[0] == "/recovery"), "")
    identity_ok = (propmap.get("ro.build.product") == EXPECTED_MODEL
                   and propmap.get("ro.build.id") == EXPECTED_BUILD
                   and propmap.get("ro.build.version.sdk") == "19")
    report = {
        "image_bytes": len(image), "image_sha256": sha256(image),
        "header_name": name, "cmdline": cmdline, "page_size": page_size,
        "kernel_size": kernel_size, "kernel_addr": f"0x{kernel_addr:08x}",
        "kernel_sha256": sha256(kernel), "stock_kernel_sha256": sha256(stock_kernel),
        "kernel_matches_stock": kernel_match,
        "ramdisk_size": ramdisk_size, "ramdisk_addr": f"0x{ramdisk_addr:08x}",
        "ramdisk_wrapper": mtk_tag, "cpio_bytes": len(cpio),
        "model": propmap.get("ro.build.product", ""),
        "build_id": propmap.get("ro.build.id", ""),
        "fingerprint": propmap.get("ro.build.fingerprint", ""),
        "customization": f"{propmap.get('ro.semc.version.cust', '')} {propmap.get('ro.semc.version.cust_revision', '')}".strip(),
        "api": propmap.get("ro.build.version.sdk", ""),
        "identity_matches_e2003_kitkat": identity_ok,
        "recovery_fstab_row": recovery_row,
        "image_fits_partition_size_only": len(image) <= partition_bytes,
        "partition_bytes_assumed": partition_bytes,
    }
    passed = identity_ok and kernel_match and bool(recovery_row) and len(image) <= partition_bytes
    return report, passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recovery_image", type=Path)
    parser.add_argument("stock_kernel_segment", type=Path,
                        help="raw kernel segment extracted offline from an E2003 stock boot image")
    parser.add_argument("--partition-bytes", type=int, default=32 * 1024 * 1024,
                        help="observed candidate partition capacity (default: 32 MiB)")
    args = parser.parse_args()
    try:
        report, passed = parse_recovery(args.recovery_image, args.stock_kernel_segment, args.partition_bytes)
    except (OSError, ValueError, struct.error, gzip.BadGzipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for key, value in report.items():
        print(f"{key}={value}")
    print("static_checks=" + ("PASS" if passed else "FAIL"))
    print("scope=offline static inspection only; not a boot, flash, mount, or restore test")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
