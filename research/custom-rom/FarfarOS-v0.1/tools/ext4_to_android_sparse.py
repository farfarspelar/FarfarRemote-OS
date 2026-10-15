#!/usr/bin/env python3
"""Create a standard Android sparse container from an exact-size raw image.

This is a packaging/analysis utility only. Sparse images are NOT validated for
the Xperia E2003 S1 bootloader and must not be flashed based on this tool.
"""

import argparse
import hashlib
import os
import struct
import sys
import zlib

MAGIC = 0xED26FF3A
CHUNK_RAW = 0xCAC1
CHUNK_DONT_CARE = 0xCAC3
BLOCK = 4096
MAX_CHUNK_BLOCKS = 256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="raw image (not modified)")
    parser.add_argument("output", help="new sparse output path")
    args = parser.parse_args()
    src = os.path.realpath(args.input)
    dst = os.path.realpath(args.output)
    if src == dst or os.path.exists(dst):
        parser.error("output must be a new path distinct from input")
    size = os.path.getsize(src)
    if size == 0 or size % BLOCK:
        parser.error("input size must be a non-zero multiple of 4096 bytes")
    total_blocks = size // BLOCK
    digest = hashlib.sha256()
    crc = 0
    chunks = 0
    out_tmp = dst + ".partial"
    if os.path.exists(out_tmp):
        parser.error("temporary output already exists: " + out_tmp)
    try:
        with open(src, "rb") as fin, open(out_tmp, "xb") as fout:
            # Android sparse v1 header; fields are patched after chunk count/CRC.
            fout.write(struct.pack("<IHHHHIIII", MAGIC, 1, 0, 28, 12,
                                   BLOCK, total_blocks, 0, 0))
            pending_kind = None
            pending = bytearray()

            def emit(kind, data, count):
                nonlocal chunks
                if kind == "zero":
                    fout.write(struct.pack("<HHII", CHUNK_DONT_CARE, 0, count, 12))
                else:
                    fout.write(struct.pack("<HHII", CHUNK_RAW, 0, count, 12 + len(data)))
                    fout.write(data)
                chunks += 1

            while True:
                block = fin.read(BLOCK)
                if not block:
                    break
                if len(block) != BLOCK:
                    raise RuntimeError("short block while reading input")
                digest.update(block)
                crc = zlib.crc32(block, crc)
                kind = "zero" if not any(block) else "raw"
                if kind != pending_kind or (kind == "raw" and len(pending) + BLOCK > MAX_CHUNK_BLOCKS * BLOCK) or (kind == "zero" and len(pending) // BLOCK >= MAX_CHUNK_BLOCKS):
                    if pending_kind is not None:
                        emit(pending_kind, pending, len(pending) // BLOCK)
                    pending_kind = kind
                    pending = bytearray()
                if kind == "raw":
                    pending.extend(block)
                else:
                    pending.extend(b"\0" * BLOCK)
            if pending_kind is not None:
                emit(pending_kind, pending, len(pending) // BLOCK)
            fout.seek(0)
            fout.write(struct.pack("<IHHHHIIII", MAGIC, 1, 0, 28, 12,
                                   BLOCK, total_blocks, chunks, crc & 0xFFFFFFFF))
            fout.flush()
            os.fsync(fout.fileno())
        os.replace(out_tmp, dst)
    except Exception:
        try:
            os.unlink(out_tmp)
        except FileNotFoundError:
            pass
        raise
    print("Input bytes:", size)
    print("Input SHA-256:", digest.hexdigest())
    print("Sparse bytes:", os.path.getsize(dst))
    sparse_digest = hashlib.sha256()
    with open(dst, "rb") as sparse_file:
        for part in iter(lambda: sparse_file.read(1024 * 1024), b""):
            sparse_digest.update(part)
    print("Sparse SHA-256:", sparse_digest.hexdigest())
    print("Blocks:", total_blocks, "chunks:", chunks, "CRC32:", format(crc & 0xFFFFFFFF, "08x"))
    print("WARNING: container/format only; E2003 bootloader acceptance is unverified.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as exc:
        print("error:", exc, file=sys.stderr)
        sys.exit(1)
