#!/usr/bin/env python3
"""Identify an MTK BootROM hardware code without loading a DA or reading flash.

This is a narrow diagnostic for a device already enumerated as Sony 0fce:f200.
It does not enter BootROM, reset the phone, disable the watchdog, access TA, or
read/write memory or partitions. It sends only the standard BROM sync sequence
and GET_HW_CODE (0xFD) query. Source/tool compatibility must still be reviewed.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path


EXPECTED_COMMIT = "7cb40e727727dfe3faa065eefb29b16ed29bbdf1"
SONY_BROM_ID = (0x0FCE, 0xF200)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def fail(message: str, status: int = 2) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mtkclient_dir", type=Path, help="clean pinned MTKClient checkout")
    args = parser.parse_args()
    checkout = args.mtkclient_dir.resolve()

    if not (checkout / "mtk.py").is_file():
        return fail("mtk.py not found in the supplied checkout")
    rev = run(["git", "-C", str(checkout), "rev-parse", "HEAD"])
    if rev.returncode or rev.stdout.strip() != EXPECTED_COMMIT:
        return fail("MTKClient checkout does not match the reviewed commit")
    dirty = run(["git", "-C", str(checkout), "status", "--porcelain"])
    if dirty.returncode or dirty.stdout.strip():
        return fail("MTKClient checkout has local modifications")

    adb = run(["adb", "devices"])
    if adb.returncode == 0:
        live = [line for line in adb.stdout.splitlines()[1:] if line.split()[-1:] in (["device"], ["unauthorized"])]
        if live:
            return fail("an Android ADB device is still online; this helper will not change its mode", 3)

    try:
        import usb.core
    except ImportError:
        return fail("PyUSB is missing; use the reviewed isolated MTKClient environment")

    try:
        matches = [d for d in usb.core.find(find_all=True) if (d.idVendor, d.idProduct) == SONY_BROM_ID]
    except Exception as exc:  # USB enumeration only; do not expose device descriptors.
        return fail(f"USB enumeration failed ({type(exc).__name__})", 3)
    if len(matches) != 1:
        return fail(f"expected exactly one Sony BROM 0fce:f200 device; found {len(matches)}", 3)

    sys.path.insert(0, str(checkout))
    try:
        from mtkclient.config.mtk_config import MtkConfig
        from mtkclient.Library.mtk_class import Mtk
        from mtkclient.Library.mtk_preloader import Preloader
        from mtkclient.Library.Port import Port

        config = MtkConfig(loglevel=logging.ERROR)
        config.vid, config.pid, config.interface = SONY_BROM_ID[0], SONY_BROM_ID[1], -1
        # The pinned checkout's Mtk.setup() assumes default_ids is a list, but
        # this commit stores it as a nested dict. Build only the exact USB Port
        # directly so we do not fall back to scanning other vendor IDs.
        mtk = Mtk(config=config, loglevel=logging.ERROR, preinit=False)
        mtk.port = Port(mtk, [[SONY_BROM_ID[0], SONY_BROM_ID[1], -1]], loglevel=logging.ERROR)
        mtk.preloader = Preloader(mtk, logging.ERROR)
        try:
            if not mtk.port.handshake(maxtries=1):
                return fail("BROM sync handshake failed; no DA or partition command was sent", 4)
            if not mtk.preloader.echo(Preloader.Cmd.GET_HW_CODE.value):
                return fail("BROM GET_HW_CODE query was not acknowledged", 4)
            # DeviceHandler.rdword() reads the 32-bit response. Do not use
            # Preloader.init(): it disables the watchdog through a register write.
            value = mtk.port.rdword()
            if value is None:
                return fail("BROM did not return a hardware code", 4)
            hwcode = (value >> 16) & 0xFFFF
            hwver = value & 0xFFFF
            print("BROM sync: PASS")
            print(f"hwcode=0x{hwcode:04x}")
            print(f"hwver=0x{hwver:04x}")
            print("No DA, register access, memory read, flash read, or flash write was requested.")
            if hwcode == 0x6752:
                print("Pinned MTKClient has an explicit 0x6752 profile; this does not prove E2003 DA/security compatibility.")
            else:
                print("STOP: this code is not the reviewed 0x6752 profile; do not run the partition-read helper.")
            return 0
        finally:
            try:
                mtk.port.close()
            except Exception:
                pass
    except Exception as exc:
        # Avoid printing USB descriptors or device-specific exception payloads.
        return fail(f"identification failed ({type(exc).__name__}); no partition operation was requested", 4)


if __name__ == "__main__":
    raise SystemExit(main())
