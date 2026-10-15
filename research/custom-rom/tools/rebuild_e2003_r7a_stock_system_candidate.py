#!/usr/bin/env python3
"""Reconstruct a stock-file-content E2003 R7A /system fallback offline.

This reverses only the two deliberate FarfarOS v0.1 mutations in the reviewed
system image: removes /system/app/FarfarRemote.apk and restores the exact
captured R7A /system/media/bootanimation.zip. It does not access a device.
The result is an ext4 file-tree reconstruction, NOT a raw backup, signed Sony
firmware, or validated flash/recovery image.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_SHA256 = "cba59c9bd76bf2f42c43f050e626c5928f0acb604ff9ce800273b56d2bcadb9d"
EXPECTED_SIZE = 2_097_152_000
EXPECTED_STOCK_ANIMATION_SHA256 = "cf580ff5826d3c0aaff7d927dd8569906fdff9a96626f73fb1ed73c8dd605445"
EXPECTED_DATA_ROOT = Path("/mnt/data/FarfarRemote-Research-POC")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, check: bool = True) -> str:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def debugfs(image: Path, commands: list[str], *, write: bool = False) -> str:
    with tempfile.NamedTemporaryFile("w", prefix="farfaros-debugfs-", dir=image.parent,
                                     delete=False) as stream:
        command_file = Path(stream.name)
        stream.write("\n".join(commands) + "\n")
    try:
        args = ["debugfs"] + (["-w"] if write else []) + ["-f", str(command_file), str(image)]
        output = run(args)
        failures = ("File not found by ext2_lookup", "Command not found", "No space left")
        if any(token in output for token in failures):
            raise RuntimeError(f"debugfs reported an operation failure:\n{output}")
        return output
    finally:
        command_file.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) != 4:
        print(f"Usage: {Path(sys.argv[0]).name} <FarfarOS-v0.1-system.ext4> <captured-R7A-bootanimation.zip> <new-output.ext4>", file=sys.stderr)
        return 2
    source, animation, output = map(Path, sys.argv[1:])
    source = source.resolve(strict=True)
    animation = animation.resolve(strict=True)
    output = output.resolve(strict=False)
    checksum = output.with_suffix(output.suffix + ".sha256")
    created_output = False
    created_checksum = False
    try:
        if output.exists():
            raise ValueError(f"refusing to overwrite output: {output}")
        if str(output).startswith(str(Path.cwd().resolve()) + os.sep):
            raise ValueError("refusing to write proprietary-derived image inside the Git repository")
        if not str(output).startswith(str(EXPECTED_DATA_ROOT) + os.sep):
            raise ValueError(f"output must be under {EXPECTED_DATA_ROOT}")
        root_dev = os.stat("/").st_dev
        data_dev = os.stat(EXPECTED_DATA_ROOT).st_dev
        if root_dev == data_dev:
            raise ValueError("data root is not on a filesystem separate from /")
        free = shutil.disk_usage(output.parent if output.parent.exists() else EXPECTED_DATA_ROOT).free
        if free < EXPECTED_SIZE + 1024 * 1024 * 1024:
            raise ValueError("need at least image size plus 1 GiB free on data filesystem")
        if source.stat().st_size != EXPECTED_SIZE or sha256(source) != SOURCE_SHA256:
            raise ValueError("source image size/hash differs from the reviewed FarfarOS v0.1 artifact")
        animation_sha = sha256(animation)
        if animation_sha != EXPECTED_STOCK_ANIMATION_SHA256:
            raise ValueError("animation is not the captured E2003 R7A stock animation")

        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="e2003-r7a-stock-candidate-", dir=output.parent) as tmp:
            work = Path(tmp)
            staged_animation = work / "bootanimation.zip"
            shutil.copyfile(animation, staged_animation)
            created_output = True
            shutil.copyfile(source, output)
            debugfs(output, [
                "rm /app/FarfarRemote.apk",
                "rm /media/bootanimation.zip",
                f"write {staged_animation} /media/bootanimation.zip",
                "sif /media/bootanimation.zip uid 0",
                "sif /media/bootanimation.zip gid 0",
                "sif /media/bootanimation.zip mode 0100644",
                "ea_set /media/bootanimation.zip security.selinux u:object_r:system_file:s0",
            ], write=True)
            readback = work / "bootanimation-readback.zip"
            debugfs(output, [f"dump /media/bootanimation.zip {readback}"])
            if sha256(readback) != EXPECTED_STOCK_ANIMATION_SHA256:
                raise ValueError("restored boot animation readback hash mismatch")
            app_listing = debugfs(output, ["ls -l /app"])
            if "FarfarRemote.apk" in app_listing:
                raise ValueError("FarfarRemote APK remains in /system/app")
            stat = debugfs(output, ["stat /media/bootanimation.zip"])
            for expected in ('Mode:  0644', 'User:     0', 'Group:     0',
                             'u:object_r:system_file:s0'):
                if expected not in stat:
                    raise ValueError(f"stock animation metadata check failed: {expected}")
            run(["e2fsck", "-fn", str(output)])

        image_hash = sha256(output)
        created_checksum = True
        checksum.write_text(f"{image_hash}  {output.name}\n")
        print(f"output={output}")
        print(f"size={output.stat().st_size}")
        print(f"sha256={image_hash}")
        print(f"restored_stock_animation_sha256={animation_sha}")
        print("validation=ext4 e2fsck clean; animation readback exact; FarfarRemote system APK absent")
        print("classification=R7A STOCK-FILE-CONTENT SYSTEM RECONSTRUCTION; NOT BYTE-EXACT BACKUP; NOT SONY-SIGNED; NOT FLASH-VALIDATED")
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        if created_output and output.exists():
            output.unlink()
        if created_checksum:
            checksum.unlink(missing_ok=True)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
