#!/usr/bin/env python3
"""Statically inspect an extracted E2003 Sony boot/FOTA ELF (no device I/O).

The tool validates the observed 32-bit ARM ELF/PT_LOAD structure and the
MediaTek 512-byte KERNEL/ROOTFS wrappers, checks the ROOTFS gzip payload, and
prints hashes and small identifying strings. The KERNEL wrapper is raw. It
does not emit firmware bytes.
Use only on locally obtained, E2003-labelled firmware candidates; the result
does not establish that a candidate matches a handset's customization.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import struct
import sys
from pathlib import Path

MTK_MAGIC = bytes.fromhex("88168858")
WRAPPER_SIZE = 512
MAX_FILE_SIZE = 64 * 1024 * 1024
EXPECTED_TAGS = (b"KERNEL", b"ROOTFS")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise ValueError(message)


def inspect(path: Path) -> list[str]:
    data = path.read_bytes()
    if not 52 <= len(data) <= MAX_FILE_SIZE or data[:4] != b"\x7fELF":
        fail("input is not a bounded ELF file")
    if data[4:7] != b"\x01\x01\x01":
        fail("expected ELF32, little-endian, version 1")
    if struct.unpack_from("<H", data, 18)[0] != 40:
        fail("expected 32-bit ARM ELF")

    entry = struct.unpack_from("<I", data, 24)[0]
    phoff = struct.unpack_from("<I", data, 28)[0]
    ehsize, phentsize, phnum = struct.unpack_from("<HHH", data, 40)
    if ehsize != 52 or phentsize != 32 or phnum != 2:
        fail("unexpected ELF header/program-header geometry")
    if phoff < ehsize or phoff + phentsize * phnum > len(data):
        fail("program-header table is outside ELF")

    segments = []
    for index in range(phnum):
        fields = struct.unpack_from("<IIIIIIII", data, phoff + index * phentsize)
        p_type, offset, vaddr, paddr, filesz, memsz, flags, align = fields
        if p_type != 1 or filesz != memsz or offset + filesz > len(data):
            fail(f"segment {index}: unsupported type, size, or file bounds")
        if filesz <= WRAPPER_SIZE:
            fail(f"segment {index}: too small for MediaTek wrapper")
        segments.append((offset, vaddr, paddr, filesz, memsz, flags, align))

    output = [f"file={path.name}", f"bytes={len(data)}", f"sha256={sha256(data)}",
              f"elf_entry=0x{entry:08x}"]
    for index, (offset, vaddr, paddr, filesz, memsz, flags, align) in enumerate(segments):
        segment = data[offset:offset + filesz]
        if segment[:4] != MTK_MAGIC:
            fail(f"segment {index}: MediaTek wrapper magic mismatch")
        declared = struct.unpack_from("<I", segment, 4)[0]
        tag = segment[8:40].split(b"\0", 1)[0]
        if tag != EXPECTED_TAGS[index] or declared != len(segment) - WRAPPER_SIZE:
            fail(f"segment {index}: unexpected {tag!r} wrapper tag/length")
        payload = segment[WRAPPER_SIZE:]
        if tag == b"ROOTFS":
            try:
                unpacked = gzip.decompress(payload)
            except (OSError, EOFError) as exc:
                fail(f"segment {index}: invalid ROOTFS gzip stream ({exc})")
        else:
            # In the observed E2003 layout KERNEL is a raw ARM zImage wrapper;
            # it is not gzip-compressed. Do not infer a different boot format.
            unpacked = payload
        if not unpacked:
            fail(f"segment {index}: empty decompressed payload")
        description = "Linux kernel payload" if tag == b"KERNEL" else "Android rootfs cpio payload"
        output.extend([
            f"segment{index}.tag={tag.decode('ascii')}",
            f"segment{index}.address=0x{paddr:08x}",
            f"segment{index}.file_bytes={filesz}",
            f"segment{index}.wrapper_sha256={sha256(segment)}",
            f"segment{index}.payload_container={'gzip' if tag == b'ROOTFS' else 'raw'}",
            f"segment{index}.stored_payload_sha256={sha256(payload)}",
            f"segment{index}.payload_bytes={len(unpacked)}",
            f"segment{index}.payload_sha256={sha256(unpacked)}",
            f"segment{index}.payload_type={description}",
        ])
        if tag == b"KERNEL":
            marker = b"Linux version "
            at = unpacked.find(marker)
            if at >= 0:
                end = unpacked.find(b"\0", at)
                output.append("kernel.version=" + unpacked[at:(end if end >= 0 else at + 160)].decode("ascii", "replace"))
        else:
            # Identifies expected init files without extracting or writing them.
            for name in (b"init.rc", b"default.prop", b"fstab"):
                output.append(f"rootfs.contains_{name.decode()}={str(name in unpacked).lower()}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path, help="extracted local E2003 boot.elf or fotakernel.elf")
    args = parser.parse_args()
    if not args.elf.is_file():
        fail("input must be an existing regular file")
    print("\n".join(inspect(args.elf)))
    print("status=STATIC_ANALYSIS_ONLY; no boot compatibility or flashability conclusion")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
