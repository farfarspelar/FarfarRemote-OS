#!/usr/bin/env python3
"""Extract and hash-check only boot.sin and fotakernel.sin from an E2003 FTF.

Offline inspection helper. It never accesses ADB/Fastboot and never writes to a
device. Firmware contents remain proprietary; keep extracted files private.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

MAX_FTF_SIZE = 4 * 1024 * 1024 * 1024
MAX_SIN_SIZE = 64 * 1024 * 1024
MAX_PAYLOAD_SIZE = 64 * 1024 * 1024
ALLOWED = ("boot.sin", "fotakernel.sin")


def fail(message: str) -> None:
    raise ValueError(message)


def extract_payload(sin: bytes, label: str) -> bytes:
    if len(sin) < 32 or sin[0] != 3 or sin[1:4] != b"SIN":
        fail(f"{label}: expected Sony SIN v3")
    header_len, payload_type, hash_type, _reserved, hash_len = struct.unpack(
        ">IIIII", sin[4:24]
    )
    if payload_type != 0x27 or hash_type != 2:
        fail(f"{label}: unsupported payload/hash type")
    if not (28 <= header_len <= len(sin)) or hash_len > header_len - 28:
        fail(f"{label}: invalid header/hash lengths")

    # Validate the hash table layout and certificate boundary. Hash records in
    # this SIN v3 profile are 4-byte lengths followed by SHA-256 digests.
    pos = 24
    records = []
    while pos < 24 + hash_len:
        if pos + 36 > 24 + hash_len:
            fail(f"{label}: truncated hash table")
        block_len = struct.unpack_from(">I", sin, pos)[0]
        digest = sin[pos + 4 : pos + 36]
        if block_len == 0:
            fail(f"{label}: zero-length hash block")
        records.append((block_len, digest))
        pos += 36
    if pos != 24 + hash_len or pos + 4 > header_len:
        fail(f"{label}: invalid hash table boundary")
    cert_len = struct.unpack_from(">I", sin, pos)[0]
    if pos + 4 + cert_len != header_len:
        fail(f"{label}: certificate does not end at declared header boundary")

    # Read the MMCF/GPTP address table; reject unknown records rather than
    # guessing at their meaning or emitting an unverified image.
    data_start = header_len
    if sin[data_start : data_start + 4] != b"MMCF":
        fail(f"{label}: missing MMCF mapping")
    mmcf_len = struct.unpack_from(">I", sin, data_start + 4)[0]
    if sin[data_start + 8 : data_start + 12] != b"GPTP":
        fail(f"{label}: missing GPTP mapping")
    gptp_len = struct.unpack_from(">I", sin, data_start + 12)[0]
    map_start = data_start + 8 + gptp_len
    map_end = data_start + 8 + mmcf_len
    if not (data_start + 16 <= map_start <= map_end <= len(sin)):
        fail(f"{label}: invalid mapping bounds")

    data_records = []
    pos = map_start
    while pos < map_end:
        if pos + 8 > map_end:
            fail(f"{label}: truncated mapping record")
        kind = sin[pos : pos + 4]
        block_len = struct.unpack_from(">I", sin, pos + 4)[0]
        if block_len < 36 or pos + block_len > map_end:
            fail(f"{label}: invalid mapping record length")
        if kind != b"ADDR" or block_len != 68:
            fail(f"{label}: unsupported mapping type {kind!r}")
        source_offset, length, output_offset = struct.unpack_from(">QQQ", sin, pos + 8)
        record_hash_type = struct.unpack_from(">I", sin, pos + 32)[0]
        digest = sin[pos + 36 : pos + 68]
        if record_hash_type != 2 or len(digest) != 32:
            fail(f"{label}: unsupported payload digest")
        data_records.append((source_offset, length, output_offset, digest))
        pos += block_len
    if pos != map_end or not data_records:
        fail(f"{label}: empty or malformed address map")

    payload_base = data_start + mmcf_len + 8
    payload_size = max(out_offset + length for _, length, out_offset, _ in data_records)
    if not (0 < payload_size <= MAX_PAYLOAD_SIZE):
        fail(f"{label}: payload size outside safety limit")
    output = bytearray(b"\xff" * payload_size)
    occupied: list[tuple[int, int]] = []
    for source_offset, length, out_offset, digest in data_records:
        start, end = payload_base + source_offset, payload_base + source_offset + length
        out_end = out_offset + length
        if length <= 0 or end > len(sin) or out_end > payload_size:
            fail(f"{label}: payload range outside file")
        if any(out_offset < old_end and out_end > old_start for old_start, old_end in occupied):
            fail(f"{label}: overlapping output ranges")
        chunk = sin[start:end]
        if hashlib.sha256(chunk).digest() != digest:
            fail(f"{label}: embedded payload SHA-256 mismatch")
        output[out_offset:out_end] = chunk
        occupied.append((out_offset, out_end))

    if output[:4] != b"\x7fELF":
        fail(f"{label}: verified payload is not an ELF image")
    if len(output) < 52 or output[4:7] != b"\x01\x01\x01":
        fail(f"{label}: unexpected ELF class/endianness")
    if struct.unpack_from("<H", output, 18)[0] != 40:
        fail(f"{label}: ELF machine is not 32-bit ARM")
    return bytes(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ftf", type=Path, help="local FTF archive to inspect")
    parser.add_argument("new_output_directory", type=Path)
    args = parser.parse_args()
    ftf = args.ftf
    output_dir = args.new_output_directory
    if not ftf.is_file() or not ftf.is_absolute():
        fail("FTF must be an existing local file; use an absolute path")
    if ftf.stat().st_size > MAX_FTF_SIZE:
        fail("FTF exceeds the 4 GiB input safety limit")
    if output_dir.exists():
        fail("output path already exists; choose a new directory")

    with zipfile.ZipFile(ftf) as archive:
        names = set(archive.namelist())
        if "META-INF/MANIFEST.MF" not in names:
            fail("FTF is missing META-INF/MANIFEST.MF")
        manifest = archive.read("META-INF/MANIFEST.MF").decode("ascii", "replace")
        metadata = {}
        for line in manifest.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
        if metadata.get("device") != "E2003":
            fail(f"refusing non-E2003 package (manifest device={metadata.get('device')!r})")
        print(
            "FTF manifest: "
            f"device={metadata.get('device')}, version={metadata.get('version')}, "
            f"branding={metadata.get('branding')}, CDA={metadata.get('cda') or '(blank)'}"
        )
        sin_data = {}
        for name in ALLOWED:
            if name not in names:
                fail(f"FTF is missing required entry {name}")
            info = archive.getinfo(name)
            if info.file_size > MAX_SIN_SIZE:
                fail(f"{name} exceeds the {MAX_SIN_SIZE}-byte entry limit")
            sin_data[name] = archive.read(info)

    extracted = [(name, extract_payload(data, name)) for name, data in sin_data.items()]
    output_dir.mkdir(parents=False, exist_ok=False)
    try:
        for name, payload in extracted:
            output = output_dir / (name[:-4] + ".elf")
            with output.open("xb") as stream:
                stream.write(payload)
            print(f"{output.name}: {len(payload)} bytes SHA-256 {hashlib.sha256(payload).hexdigest()}")
    except Exception:
        # Do not leave partial output that could be mistaken for a complete set.
        for item in output_dir.iterdir():
            item.unlink()
        output_dir.rmdir()
        raise
    print("Offline extraction complete. These images are proprietary; do not flash based on this result.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, zipfile.BadZipFile, KeyError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
