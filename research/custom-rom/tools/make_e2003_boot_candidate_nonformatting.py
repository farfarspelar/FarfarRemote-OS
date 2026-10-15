#!/usr/bin/env python3
"""Create an offline E2003 boot-container variant with risky actions omitted.

This is a local experiment artifact only. It removes Sony one-shot
wipe/reset/TA-update actions and the protect1/protect2 fstab mount entries from
the existing candidate ramdisk. That deliberately changes Sony startup behavior
and may prevent boot. It does not prove the result is safe, bootable, or
appropriate to flash. No device I/O.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import re
import struct
import sys
from pathlib import Path

ANDROID_MAGIC = b"ANDROID!"
MTK_MAGIC = bytes.fromhex("88168858")
PAGE = 2048
SOURCE_SHA256 = "80d51e07d4f5d7151cc7899833aed246539c23ab306412169c622390509d8182"
DISABLED_FILES = {
    "init.sony-bootstrap-wipedata.rc": b"# FarfarOS offline experiment: automatic wipedata action omitted.\n",
    "init.sony-bootstrap-mr.rc": b"# FarfarOS offline experiment: automatic master-reset action omitted.\n",
    "init.sony-bootstrap-updatemiscta.rc": b"# FarfarOS offline experiment: automatic MiscTA update service omitted.\n",
}
REMOVED_ACTION = re.compile(
    rb"^\s*(?:start\s+(?:mr|wipedata|updatemiscta)\b|"
    rb"exec\s+/system/bin/(?:mr|wipedata)\b)", re.MULTILINE
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align(n: int, boundary: int) -> int:
    return (n + boundary - 1) // boundary * boundary


def parse_newc(raw: bytes) -> list[tuple[bytearray, bytes, bytes]]:
    records = []
    pos = 0
    while pos + 110 <= len(raw):
        header = bytearray(raw[pos:pos + 110])
        if header[:6] not in (b"070701", b"070702"):
            raise ValueError(f"invalid newc header at byte {pos}")
        fields = [int(header[6 + 8 * i:14 + 8 * i], 16) for i in range(13)]
        size, namesize = fields[6], fields[11]
        pos += 110
        if namesize < 1 or pos + namesize > len(raw):
            raise ValueError("invalid cpio name length")
        name = raw[pos:pos + namesize]
        if not name.endswith(b"\0"):
            raise ValueError("unterminated cpio name")
        pos = align(pos + namesize, 4)
        if size > len(raw) - pos:
            raise ValueError("invalid cpio payload length")
        payload = raw[pos:pos + size]
        pos = align(pos + size, 4)
        records.append((header, name, payload))
        if name.rstrip(b"\0") in (b"TRAILER!!!", b"./TRAILER!!!"):
            if pos != len(raw) and any(raw[pos:]):
                raise ValueError("unexpected non-padding bytes after cpio trailer")
            return records
    raise ValueError("cpio archive has no trailer")


def write_field(header: bytearray, index: int, value: int) -> None:
    header[6 + 8 * index:14 + 8 * index] = f"{value:08x}".encode("ascii")


def pack_newc(records: list[tuple[bytearray, bytes, bytes]]) -> bytes:
    result = bytearray()
    for header, name, payload in records:
        write_field(header, 6, len(payload))
        if header[:6] == b"070702":
            write_field(header, 12, sum(payload) & 0xFFFFFFFF)
        result.extend(header)
        result.extend(name)
        result.extend(bytes(align(len(result), 4) - len(result)))
        result.extend(payload)
        result.extend(bytes(align(len(result), 4) - len(result)))
    return bytes(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="current offline Android boot-container candidate")
    parser.add_argument("output", type=Path, help="new output path outside the Git repository")
    args = parser.parse_args()
    try:
        source = args.source.resolve(strict=True)
        output = args.output.resolve(strict=False)
        repo = Path(__file__).resolve().parents[3]
        if output.exists() or output.is_relative_to(repo):
            raise ValueError("output must be new and outside the Git repository")
        data_root = Path(os.environ.get("FARFAR_DATA_ROOT", "/mnt/data")).resolve(strict=True)
        if not data_root.is_dir() or not output.is_relative_to(data_root):
            raise ValueError(f"output must be under the mounted data volume {data_root}")
        if data_root.stat().st_dev == Path("/").stat().st_dev:
            raise ValueError("data root resolves to the system filesystem; refusing output")
        image = source.read_bytes()
        if sha(image) != SOURCE_SHA256:
            raise ValueError("source image hash differs from the reviewed E2003 kernel candidate")
        if len(image) < PAGE or image[:8] != ANDROID_MAGIC:
            raise ValueError("source is not an Android legacy boot image")
        values = list(struct.unpack_from("<10I", image, 8))
        kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page, dt_size, unused = values
        if page != PAGE or second_size or dt_size:
            raise ValueError("unsupported boot header geometry")
        kernel_start = PAGE
        ramdisk_start = kernel_start + align(kernel_size, PAGE)
        ramdisk_end = ramdisk_start + ramdisk_size
        if kernel_size == 0 or ramdisk_end > len(image):
            raise ValueError("boot image segment bounds are invalid")
        kernel = image[kernel_start:kernel_start + kernel_size]
        wrapper = image[ramdisk_start:ramdisk_end]
        if len(wrapper) < 512 or wrapper[:4] != MTK_MAGIC or wrapper[8:40].split(b"\0", 1)[0] != b"ROOTFS":
            raise ValueError("ramdisk is not the expected MediaTek ROOTFS wrapper")
        declared = struct.unpack_from("<I", wrapper, 4)[0]
        if declared != len(wrapper) - 512:
            raise ValueError("MediaTek ROOTFS wrapper length mismatch")
        cpio_data = gzip.decompress(wrapper[512:])
        original = parse_newc(cpio_data)
        final = []
        found: set[str] = set()
        changed: list[str] = []
        for header, name_raw, payload in original:
            name = name_raw[:-1].decode("utf-8", "replace").removeprefix("./")
            if name in DISABLED_FILES:
                found.add(name)
                new_payload = DISABLED_FILES[name]
                if payload != new_payload:
                    changed.append(name)
                payload = new_payload
            elif name == "fstab":
                found.add("fstab")
                lines = payload.splitlines(keepends=True)
                patched = []
                for line in lines:
                    if b"/by-name/protect1" in line or b"/by-name/protect2" in line:
                        if b"autoformat" not in line:
                            raise ValueError("protect partition fstab row did not match expected source")
                        changed.append("removed protect1/protect2 fstab mounts")
                        continue
                    patched.append(line)
                payload = b"".join(patched)
            final.append((header, name_raw, payload))
        expected = set(DISABLED_FILES) | {"fstab"}
        if found != expected:
            raise ValueError(f"ramdisk missing expected files: {sorted(expected - found)}")
        cpio_out = pack_newc(final)
        # Deterministic gzip wrapper: no host timestamp.
        gzip_out = gzip.compress(cpio_out, compresslevel=9, mtime=0)
        wrapper_out = bytearray(wrapper[:512]) + gzip_out
        struct.pack_into("<I", wrapper_out, 4, len(gzip_out))
        values[2] = len(wrapper_out)
        header = bytearray(image[:PAGE])
        struct.pack_into("<10I", header, 8, *values)
        new_id = hashlib.sha1(
            kernel + struct.pack("<I", len(kernel)) + wrapper_out + struct.pack("<I", len(wrapper_out))
            + struct.pack("<I", 0)
        ).digest()
        header[576:608] = new_id + bytes(32 - len(new_id))
        rebuilt = bytearray(header)
        rebuilt.extend(kernel)
        rebuilt.extend(bytes(align(len(rebuilt), PAGE) - len(rebuilt)))
        rebuilt.extend(wrapper_out)
        rebuilt.extend(bytes(align(len(rebuilt), PAGE) - len(rebuilt)))
        # Reparse and assert disabled operations cannot be invoked via these imports.
        verify_entries = parse_newc(gzip.decompress(bytes(wrapper_out[512:])))
        verify_files = {n[:-1].decode("utf-8", "replace").removeprefix("./"): p for _, n, p in verify_entries}
        if any(b"/by-name/protect1" in line or b"/by-name/protect2" in line
               for line in verify_files["fstab"].splitlines()):
            raise ValueError("protect partition fstab mount remains")
        for name in DISABLED_FILES:
            if b"exec /system/bin/" in verify_files[name] or b"start updatemiscta" in verify_files[name]:
                raise ValueError(f"automatic action remains in {name}")
        for name, payload in verify_files.items():
            if name.endswith(".rc") and name not in DISABLED_FILES and REMOVED_ACTION.search(payload):
                raise ValueError(f"another ramdisk init script invokes a removed action: {name}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as stream:
            stream.write(rebuilt)
        print(f"output={output}")
        print(f"bytes={len(rebuilt)}")
        print(f"sha256={sha(rebuilt)}")
        print(f"source_sha256={sha(image)}")
        print("disabled_actions=" + ",".join(sorted(set(changed))))
        print("status=OFFLINE EXPERIMENTAL BOOT CONTAINER; NOT BOOT-TESTED OR FLASHABLE")
        print("warning=Sony bootstrap behavior and protect partition mounts were changed; boot compatibility is unknown")
        return 0
    except (OSError, ValueError, struct.error, gzip.BadGzipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
