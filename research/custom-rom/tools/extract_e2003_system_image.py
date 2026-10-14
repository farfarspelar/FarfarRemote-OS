#!/usr/bin/env python3
"""Verify and extract only system.sin from a local E2003 Sony FTF.

Offline-only: no ADB/Fastboot, no device writes. Extracted proprietary images
must remain private and outside Git. This does not establish firmware/CDA
compatibility and is not a flashing tool.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

MAX_FTF_SIZE = 4 * 1024**3
MAX_SIN_SIZE = 3 * 1024**3
MAX_HEADER_SIZE = 16 * 1024**2
# Live E2003 /system partition: 2,048,000 KiB, obtained read-only over ADB.
MAX_SYSTEM_IMAGE_SIZE = 2_097_152_000
CHUNK_SIZE = 1024 * 1024


def fail(message: str) -> None:
    raise ValueError(message)


def read_exact(stream, size: int, label: str) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        fail(f"truncated {label}")
    return data


def parse_header(stream, sin_size: int):
    prefix = read_exact(stream, 24, "SIN header")
    if prefix[:4] != b"\x03SIN":
        fail("system.sin is not Sony SIN v3")
    header_len, payload_type, hash_type, _reserved, hash_len = struct.unpack(
        ">IIIII", prefix[4:24]
    )
    if payload_type != 0x27 or hash_type != 2:
        fail("unsupported SIN payload/hash type")
    if not (28 <= header_len <= min(MAX_HEADER_SIZE, sin_size)):
        fail("SIN header length outside safety limits")
    if hash_len > header_len - 28:
        fail("invalid SIN hash table length")

    remainder = read_exact(stream, header_len - 24, "SIN header body")
    hashes: list[tuple[int, bytes]] = []
    pos = 0
    hash_end = hash_len
    while pos < hash_end:
        if pos + 36 > hash_end:
            fail("truncated SIN hash table")
        length = struct.unpack_from(">I", remainder, pos)[0]
        digest = remainder[pos + 4 : pos + 36]
        if length == 0:
            fail("zero-length SIN integrity block")
        hashes.append((length, digest))
        pos += 36
    if pos != hash_end or pos + 4 > len(remainder):
        fail("invalid SIN hash table/certificate boundary")
    cert_len = struct.unpack_from(">I", remainder, pos)[0]
    if pos + 4 + cert_len != len(remainder):
        fail("SIN certificate does not end at declared header boundary")
    if sum(length for length, _ in hashes) != sin_size - header_len:
        fail("SIN integrity blocks do not cover the complete post-header data")
    return header_len, hashes


def parse_map(stream, header_len: int, sin_size: int):
    stream.seek(header_len)
    fixed = read_exact(stream, 16, "MMCF/GPTP headers")
    if fixed[:4] != b"MMCF" or fixed[8:12] != b"GPTP":
        fail("missing MMCF/GPTP map")
    mmcf_len = struct.unpack_from(">I", fixed, 4)[0]
    gptp_len = struct.unpack_from(">I", fixed, 12)[0]
    if not (16 <= mmcf_len <= MAX_HEADER_SIZE and 16 <= gptp_len <= mmcf_len):
        fail("mapping table lengths outside safety limits")
    stream.seek(header_len)
    # SIN stores the MMCF record-area length without its leading 8-byte header.
    mapping = read_exact(stream, mmcf_len + 8, "MMCF mapping")
    if mapping[:4] != b"MMCF" or mapping[8:12] != b"GPTP":
        fail("mapping changed while reading")

    records = []
    pos = 8 + gptp_len
    map_end = mmcf_len + 8
    while pos < map_end:
        if pos + 8 > map_end:
            fail("truncated address-map record")
        kind = mapping[pos : pos + 4]
        record_len = struct.unpack_from(">I", mapping, pos + 4)[0]
        if kind != b"ADDR" or record_len != 68 or pos + record_len > map_end:
            fail("unsupported or malformed system SIN mapping record")
        source, length, output = struct.unpack_from(">QQQ", mapping, pos + 8)
        digest_type = struct.unpack_from(">I", mapping, pos + 32)[0]
        digest = mapping[pos + 36 : pos + 68]
        if digest_type != 2 or length == 0:
            fail("unsupported mapping digest or empty range")
        records.append((source, length, output, digest))
        pos += record_len
    if not records:
        fail("empty system image address map")

    payload_base = header_len + mmcf_len + 8
    mapped_size = max(output + length for _, length, output, _ in records)
    if mapped_size > MAX_SYSTEM_IMAGE_SIZE:
        fail("mapped image exceeds the observed E2003 /system partition size")
    # The map omits trailing erased blocks. Reconstruct the full live
    # partition-sized image so ext4's own declared block count is addressable.
    image_size = MAX_SYSTEM_IMAGE_SIZE
    previous_src_end = 0
    output_ranges = []
    for source, length, output, _ in records:
        if source < previous_src_end or payload_base + source + length > sin_size:
            fail("overlapping, unsorted, or out-of-file source map")
        previous_src_end = source + length
        output_ranges.append((output, output + length))
    output_ranges.sort()
    if any(output_ranges[i][0] < output_ranges[i - 1][1] for i in range(1, len(output_ranges))):
        fail("overlapping output map ranges")
    return mapping, payload_base, image_size, records


def verify_and_extract(stream, sin_size: int, output: Path) -> tuple[int, str, str]:
    stream.seek(0)
    header_len, hash_blocks = parse_header(stream, sin_size)
    _, payload_base, image_size, maps = parse_map(stream, header_len, sin_size)

    output.parent.mkdir(parents=False, exist_ok=True)
    digest_all = hashlib.sha256()
    map_index = 0
    map_hash = hashlib.sha256()
    map_bytes = 0
    absolute = header_len
    block_index = 0
    block_remaining = hash_blocks[0][0]
    block_hash = hashlib.sha256()

    # SIN address-map gaps reconstruct as zero-filled holes in the raw ext4
    # image. Preserve the filesystem's declared partition-sized extent.
    try:
        with output.open("x+b") as target:
            fill = b"\x00" * CHUNK_SIZE
            remaining = image_size
            while remaining:
                part = fill[: min(remaining, len(fill))]
                target.write(part)
                remaining -= len(part)

            stream.seek(header_len)
            tail_remaining = sin_size - header_len
            while tail_remaining:
                data = read_exact(stream, min(CHUNK_SIZE, tail_remaining), "SIN payload")
                digest_all.update(data)
                cursor = 0
                while cursor < len(data):
                    amount = min(len(data) - cursor, block_remaining)
                    block_hash.update(data[cursor : cursor + amount])
                    cursor += amount
                    block_remaining -= amount
                    if block_remaining == 0:
                        expected = hash_blocks[block_index][1]
                        if block_hash.digest() != expected:
                            fail(f"SIN integrity hash mismatch at block {block_index}")
                        block_index += 1
                        if block_index < len(hash_blocks):
                            block_remaining = hash_blocks[block_index][0]
                            block_hash = hashlib.sha256()

                # Copy only ranges listed by ADDR records while hashing each
                # mapped range against the digest embedded in that record.
                data_start, data_end = absolute, absolute + len(data)
                while map_index < len(maps):
                    source, length, out_offset, expected = maps[map_index]
                    start = payload_base + source
                    end = start + length
                    left, right = max(data_start, start), min(data_end, end)
                    if left < right:
                        piece = data[left - data_start : right - data_start]
                        map_hash.update(piece)
                        map_bytes += len(piece)
                        target.seek(out_offset + left - start)
                        target.write(piece)
                    if data_end >= end:
                        if map_bytes != length or map_hash.digest() != expected:
                            fail(f"mapped image SHA-256 mismatch at address record {map_index}")
                        map_index += 1
                        map_hash = hashlib.sha256()
                        map_bytes = 0
                    else:
                        break

                absolute += len(data)
                tail_remaining -= len(data)

            if block_index != len(hash_blocks) or map_index != len(maps):
                fail("SIN ended before all integrity/address records were verified")
            target.flush()
            target.seek(0)
            image_hash = hashlib.sha256()
            while True:
                chunk = target.read(CHUNK_SIZE)
                if not chunk:
                    break
                image_hash.update(chunk)
        return image_size, image_hash.hexdigest(), digest_all.hexdigest()
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ftf", type=Path, help="local E2003 FTF file")
    parser.add_argument("output", type=Path, help="new private system.img path outside Git")
    args = parser.parse_args()
    ftf, output = args.ftf, args.output
    if not ftf.is_absolute() or not ftf.is_file():
        fail("FTF must be an existing absolute path")
    if ftf.stat().st_size > MAX_FTF_SIZE:
        fail("FTF exceeds 4 GiB safety limit")
    if not output.is_absolute() or output.exists() or not output.parent.is_dir():
        fail("output must be a new absolute file in an existing directory")
    if output.resolve().is_relative_to(Path.cwd().resolve()):
        fail("refusing to write proprietary firmware content inside the repository")

    with zipfile.ZipFile(ftf) as archive:
        if "META-INF/MANIFEST.MF" not in archive.namelist() or "system.sin" not in archive.namelist():
            fail("FTF must contain a manifest and system.sin")
        manifest = archive.read("META-INF/MANIFEST.MF").decode("ascii", "replace")
        metadata = {}
        for line in manifest.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
        if metadata.get("device") != "E2003":
            fail(f"refusing non-E2003 FTF (device={metadata.get('device')!r})")
        if not (metadata.get("version") or "").startswith("25.0.A.2.31"):
            fail("FTF build is not 25.0.A.2.31")
        info = archive.getinfo("system.sin")
        if info.file_size > MAX_SIN_SIZE:
            fail("system.sin exceeds 3 GiB safety limit")
        print(
            "FTF label: "
            f"device={metadata.get('device')} version={metadata.get('version')} "
            f"branding={metadata.get('branding')} CDA={metadata.get('cda') or '(blank)'}"
        )
        with archive.open(info) as sin:
            size, image_digest, sin_digest = verify_and_extract(sin, info.file_size, output)
    print(f"Verified mapped system image: {size} bytes SHA-256 {image_digest}")
    print(f"Verified SIN post-header SHA-256: {sin_digest}")
    print(f"Private output: {output}")
    print("This is an unmatched analysis candidate; extraction does not imply device compatibility.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, zipfile.BadZipFile, KeyError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
