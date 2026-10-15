#!/usr/bin/env python3
"""Make a host-only diagnostic boot-container variant without apps_log init.

The input is the pinned, already modified E2003 kernel candidate. This removes
the complete init.mt6752.rc apps_log setup block so this candidate will not run
e2fsck/tune2fs or mount that partition. It is experimental and not for booting
or flashing: the R10A ramdisk is not matched to the live R7A handset.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import struct
import sys
from pathlib import Path

SOURCE_SHA256 = "fde40f857262b04a48d98662069c2e3e134ad6330cb288f6894df55a9f79cbfb"
ANDROID_MAGIC = b"ANDROID!"
PAGE = 2048
MTK_MAGIC = bytes.fromhex("88168858")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align(n: int, boundary: int) -> int:
    return (n + boundary - 1) // boundary * boundary


def unpack_newc(raw: bytes):
    entries = []
    pos = 0
    while pos + 110 <= len(raw):
        header = bytearray(raw[pos:pos + 110])
        if header[:6] not in (b"070701", b"070702"):
            raise ValueError(f"invalid newc header at {pos}")
        fields = [int(header[6 + 8 * i:14 + 8 * i], 16) for i in range(13)]
        size, namesize = fields[6], fields[11]
        pos += 110
        if namesize < 1 or pos + namesize > len(raw):
            raise ValueError("invalid cpio name size")
        name = raw[pos:pos + namesize]
        if not name.endswith(b"\0"):
            raise ValueError("unterminated cpio filename")
        pos = align(pos + namesize, 4)
        if size > len(raw) - pos:
            raise ValueError("invalid cpio payload size")
        payload = raw[pos:pos + size]
        pos = align(pos + size, 4)
        entries.append((header, name, payload))
        if name.rstrip(b"\0") in (b"TRAILER!!!", b"./TRAILER!!!"):
            if any(raw[pos:]):
                raise ValueError("unexpected bytes after cpio trailer")
            return entries
    raise ValueError("cpio trailer not found")


def pack_newc(entries) -> bytes:
    out = bytearray()
    for header, name, payload in entries:
        header[54:62] = f"{len(payload):08x}".encode("ascii")
        if header[:6] == b"070702":
            header[102:110] = f"{sum(payload) & 0xffffffff:08x}".encode("ascii")
        out.extend(header)
        out.extend(name)
        out.extend(bytes(align(len(out), 4) - len(out)))
        out.extend(payload)
        out.extend(bytes(align(len(out), 4) - len(out)))
    return bytes(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    try:
        source = args.source.resolve(strict=True)
        output = args.output.resolve(strict=False)
        repo = Path(__file__).resolve().parents[3]
        data_root = Path(os.environ.get("FARFAR_DATA_ROOT", "/mnt/data")).resolve(strict=True)
        if output.exists() or output.is_relative_to(repo) or not output.is_relative_to(data_root):
            raise ValueError("output must be a new file under /mnt/data and outside Git")
        if data_root.stat().st_dev == Path("/").stat().st_dev:
            raise ValueError("/mnt/data is not on a separate mounted filesystem")
        image = source.read_bytes()
        if sha(image) != SOURCE_SHA256:
            raise ValueError("source hash differs from the reviewed diagnostic candidate")
        if image[:8] != ANDROID_MAGIC or len(image) < PAGE:
            raise ValueError("input is not an Android legacy boot container")
        values = list(struct.unpack_from("<10I", image, 8))
        ksize, _, rsize, _, second_size, _, _, page, dt_size, _ = values
        if page != PAGE or second_size or dt_size:
            raise ValueError("unexpected boot header geometry")
        kstart = PAGE
        rstart = kstart + align(ksize, PAGE)
        rend = rstart + rsize
        kernel, wrapper = image[kstart:kstart + ksize], image[rstart:rend]
        if len(wrapper) < 512 or wrapper[:4] != MTK_MAGIC or wrapper[8:40].split(b"\0", 1)[0] != b"ROOTFS":
            raise ValueError("unexpected MediaTek ROOTFS wrapper")
        compressed = wrapper[512:]
        if struct.unpack_from("<I", wrapper, 4)[0] != len(compressed):
            raise ValueError("ROOTFS wrapper length mismatch")
        entries = unpack_newc(gzip.decompress(compressed))
        changed = 0
        verified: dict[str, bytes] = {}
        output_entries = []
        for header, raw_name, payload in entries:
            name = raw_name[:-1].decode("utf-8", "replace").removeprefix("./")
            if name == "init.mt6752.rc":
                lines = payload.splitlines(keepends=True)
                kept = []
                inside = False
                seen = 0
                for line in lines:
                    if line.strip() == b"#mount apps_log block":
                        if inside:
                            raise ValueError("nested apps_log block marker")
                        inside = True
                        seen += 1
                        continue
                    if inside and line.strip() == b"#mount end":
                        inside = False
                        seen += 1
                        continue
                    if inside:
                        changed += 1
                        continue
                    kept.append(line)
                if inside or seen != 2 or changed < 1:
                    raise ValueError("expected complete apps_log init block was not found")
                payload = b"".join(kept)
            verified[name] = payload
            output_entries.append((header, raw_name, payload))
        if "init.mt6752.rc" not in verified:
            raise ValueError("init.mt6752.rc missing")
        if b"apps_log" in verified["init.mt6752.rc"] or b"/mnt/idd" in verified["init.mt6752.rc"]:
            raise ValueError("apps_log init references remain")
        if any((b"apps_log" in data or b"/mnt/idd" in data) for n, data in verified.items() if n.endswith(".rc")):
            raise ValueError("another init rc references apps_log")

        cpio = pack_newc(output_entries)
        gz = gzip.compress(cpio, compresslevel=9, mtime=0)
        new_wrapper = bytearray(wrapper[:512]) + gz
        struct.pack_into("<I", new_wrapper, 4, len(gz))
        values[2] = len(new_wrapper)
        header = bytearray(image[:PAGE])
        struct.pack_into("<10I", header, 8, *values)
        digest = hashlib.sha1(kernel + struct.pack("<I", len(kernel)) + new_wrapper + struct.pack("<I", len(new_wrapper)) + struct.pack("<I", 0)).digest()
        header[576:608] = digest + bytes(32 - len(digest))
        rebuilt = bytearray(header)
        rebuilt.extend(kernel)
        rebuilt.extend(bytes(align(len(rebuilt), PAGE) - len(rebuilt)))
        rebuilt.extend(new_wrapper)
        rebuilt.extend(bytes(align(len(rebuilt), PAGE) - len(rebuilt)))
        # Round-trip parser check and unchanged kernel check before writing.
        check = unpack_newc(gzip.decompress(bytes(new_wrapper[512:])))
        check_map = {n[:-1].decode("utf-8", "replace").removeprefix("./"): p for _, n, p in check}
        if check_map["init.mt6752.rc"] != verified["init.mt6752.rc"]:
            raise ValueError("init ramdisk round-trip mismatch")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as f:
            f.write(rebuilt)
        print(f"output={output}")
        print(f"bytes={len(rebuilt)}")
        print(f"sha256={sha(rebuilt)}")
        print(f"source_sha256={sha(image)}")
        print(f"removed_apps_log_init_lines={changed}")
        print("status=OFFLINE DIAGNOSTIC ONLY; R10A RAMDISK; NOT BOOT-TESTED OR FLASHABLE")
        return 0
    except (OSError, ValueError, struct.error, gzip.BadGzipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
