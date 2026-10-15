#!/usr/bin/env python3
"""Build a local R7A /system ext4 POC from the inspected E2003 R10A image.

Inputs (all local; the live metadata is read-only output from the capture tool):
  R10A ext4 image, its extracted file tree, an ADB-pulled R7A /system tree,
  captured E2003 R7A metadata, FarfarRemote OS APK, output image.

No device commands are run. The generated image is not Sony-signed, packaged,
booted, or suitable for flashing.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SOURCE_SHA256 = "931878c1f851ee55db08eb6cc6bd39a49b28d9e56d57067a85e64415f9c1a949"
APK_CERT_SHA256 = "63F9336D0038B8EBE9AC8224F8869E1F871828D81B6269372315CE055CF607FD"
ENTRY = re.compile(r"^([bcdlps-][rwxStTs-]{9})\s+(\S+)\s+(\S+)\s+(u:object_r:[^\s]+)\s+(.*)$")
TYPE = {"regular": "-", "directory": "d", "symlink": "l", "character": "c", "block": "b", "fifo": "p", "socket": "s"}
UID = {"root": 0, "shell": 2000, "dhcp": 1014}
GID = {"root": 0, "shell": 2000, "system": 1000, "inet": 3003}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mode_bits(text: str) -> int:
    bits = (0o400, 0o200, 0o100, 0o040, 0o020, 0o010, 0o004, 0o002, 0o001)
    value = 0
    for char, bit in zip(text[1:], bits):
        if char in "rwxst" or (char in "sS" and bit in (0o100, 0o010)) or (char in "tT" and bit == 0o001):
            value |= bit
    if text[3] in "sS": value |= 0o4000
    if text[6] in "sS": value |= 0o2000
    if text[9] in "tT": value |= 0o1000
    return value


def live_manifest(path: Path) -> dict[str, dict[str, object]]:
    headers: dict[str, str] = {}
    entries = {}
    current = None
    for raw in path.read_text(errors="replace").splitlines():
        if raw.startswith("# target_") and "=" in raw:
            key, value = raw[2:].split("=", 1)
            headers[key] = value
            continue
        if raw.startswith("/") and raw.endswith(":"):
            current = raw[:-1]
            continue
        match = ENTRY.match(raw)
        if not match or current is None:
            continue
        permissions, owner, group, label, name = match.groups()
        if name in (".", ".."):
            continue
        target = ""
        if permissions[0] == "l" and " -> " in name:
            name, target = name.split(" -> ", 1)
        rel = (current + "/" + name).removeprefix("/system")
        if rel == "/" or any(c.isspace() for c in rel) or '"' in rel:
            raise ValueError(f"Unsupported system path: {rel!r}")
        if owner not in UID or group not in GID:
            raise ValueError(f"Unknown Android owner/group for {rel}: {owner}:{group}")
        entries[rel] = {
            "type": permissions[0], "mode": mode_bits(permissions),
            "uid": UID[owner], "gid": GID[group], "label": label,
            "target": target,
        }
    expected = {"target_model": "E2003", "target_build": "25.0.A.2.31",
                "target_cda": "1293-7358", "target_revision": "R7A"}
    for key, value in expected.items():
        if headers.get(key) != value:
            raise ValueError(f"metadata header {key} must be {value!r}")
    if not entries:
        raise ValueError("No R7A system entries found in metadata")
    return entries


def index_tree(root: Path) -> tuple[dict[str, dict[str, object]], set[str]]:
    root = root.resolve(strict=True)
    files: dict[str, dict[str, object]] = {}
    directories = {"/"}
    for current, dirs, names in os.walk(root, followlinks=False):
        rel_current = "/" + Path(current).relative_to(root).as_posix()
        if rel_current == "/.": rel_current = "/"
        for name in list(dirs):
            item = Path(current) / name
            rel = (rel_current.rstrip("/") + "/" + name) if rel_current != "/" else "/" + name
            if item.is_symlink():
                files[rel] = {"type": "l", "target": os.readlink(item)}
                dirs.remove(name)
            else:
                directories.add(rel)
        for name in names:
            item = Path(current) / name
            rel = (rel_current.rstrip("/") + "/" + name) if rel_current != "/" else "/" + name
            if item.is_symlink():
                files[rel] = {"type": "l", "target": os.readlink(item)}
            elif item.is_file():
                files[rel] = {"type": "-", "sha256": digest(item), "size": item.stat().st_size, "host": item}
    return files, directories


def ensure_tools(aapt2: str) -> None:
    for tool in ("debugfs", "e2fsck", "file", "keytool", "jarsigner", "sha256sum"):
        if shutil.which(tool) is None:
            raise RuntimeError(f"Required tool not found: {tool}")
    if not Path(aapt2).is_file() or not os.access(aapt2, os.X_OK):
        raise RuntimeError("Set AAPT2_BIN to an executable Android SDK aapt2")


def validate_apk(apk: Path, aapt2: str) -> None:
    badging = subprocess.check_output([aapt2, "dump", "badging", str(apk)], text=True)
    if "package: name='org.farfarremote'" not in badging or "minSdkVersion:'19'" not in badging:
        raise ValueError("APK must be FarfarRemote OS (org.farfarremote), minSdkVersion 19")
    cert_output = subprocess.check_output(["keytool", "-printcert", "-jarfile", str(apk)], text=True, stderr=subprocess.DEVNULL)
    match = re.search(r"SHA256:\s*([0-9A-Fa-f:]+)", cert_output)
    if not match or match.group(1).replace(":", "").upper() != APK_CERT_SHA256:
        raise ValueError("APK signer differs from the OS APK already installed on the E2003")
    subprocess.run(["jarsigner", "-verify", str(apk)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def validate_bootanimation(path: Path) -> None:
    """Validate the supplied E2003-sized intro + loop animation archive."""
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError("bootanimation ZIP CRC validation failed")
            names = set(archive.namelist())
            if "desc.txt" not in names:
                raise ValueError("bootanimation archive has no root desc.txt")
            required = {f"part0/{i:04d}.png" for i in range(8)} | {f"part1/{i:04d}.png" for i in range(6)}
            if not required <= names:
                raise ValueError("bootanimation archive is missing expected intro/loop frames")
            desc = archive.read("desc.txt").decode("ascii").splitlines()
            if desc != ["540 960 18", "p 1 0 part0", "p 0 0 part1"]:
                raise ValueError("bootanimation desc.txt differs from the inspected E2003 animation")
            for name in sorted(n for n in names if n.endswith(".png")):
                data = archive.read(name)
                if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
                    raise ValueError(f"invalid PNG frame: {name}")
                if struct.unpack(">II", data[16:24]) != (540, 960):
                    raise ValueError(f"unexpected bootanimation frame dimensions: {name}")
    except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid bootanimation archive: {exc}") from exc


def run_debugfs(image: Path, commands: list[str], work: Path) -> str:
    command_file = work / "debugfs.commands"
    command_file.write_text("\n".join(commands) + "\n")
    proc = subprocess.run(["debugfs", "-w", "-f", str(command_file), str(image)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = proc.stdout + "\n" + proc.stderr
    errors = [line for line in output.splitlines()
              if any(token in line for token in ("File not found", "Command not found", "Usage:", "Could not", "No space left"))]
    if proc.returncode != 0 or errors:
        raise RuntimeError("debugfs update failed: " + " | ".join(errors[:8] or [proc.stderr.strip()]))
    return output


def read_debugfs(image: Path, commands: list[str], work: Path) -> str:
    command_file = work / "debugfs-read.commands"
    command_file.write_text("\n".join(commands) + "\n")
    proc = subprocess.run(["debugfs", "-f", str(command_file), str(image)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"read-only debugfs failed (exit {proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout + "\n" + proc.stderr


def main() -> int:
    if len(sys.argv) not in (7, 8):
        print(f"Usage: {Path(sys.argv[0]).name} <R10A-system.ext4> <R10A-extracted-tree> <R7A-system-tree> <R7A-metadata.txt> <FarfarRemote-OS.apk> <output.ext4> [bootanimation.zip]", file=sys.stderr)
        return 2
    source, stock_root, live_root, metadata, apk, output = map(Path, sys.argv[1:7])
    bootanimation = Path(sys.argv[7]) if len(sys.argv) == 8 else None
    aapt2 = os.environ.get("AAPT2_BIN", "")
    try:
        ensure_tools(aapt2)
        if any(not path.exists() for path in (source, stock_root, live_root, metadata, apk)) or (bootanimation is not None and not bootanimation.is_file()):
            raise ValueError("One or more input paths do not exist")
        repo = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        if str(output.resolve(strict=False)).startswith(repo + os.sep):
            raise ValueError("Refusing to write a firmware image inside the Git repository")
        if output.exists() or output.resolve(strict=False) in (source.resolve(), apk.resolve()):
            raise ValueError("Output must be a new path distinct from inputs")
        if digest(source) != SOURCE_SHA256:
            raise ValueError("source system image hash does not match inspected E2003 R10A image")
        live = live_manifest(metadata)
        stock_files, stock_dirs = index_tree(stock_root)
        live_dirs = {path for path, entry in live.items() if entry["type"] == "d"} | {"/"}

        # The ADB pull can contain extra paths from following /vendor -> /system/vendor.
        # Only the captured device manifest defines the actual E2003 /system paths.
        live_tree: dict[str, dict[str, object]] = {}
        for path, entry in live.items():
            if entry["type"] == "-":
                item = live_root / path.lstrip("/")
                if not item.is_file():
                    raise ValueError(f"R7A file missing from captured tree: {path}")
                live_tree[path] = {"type": "-", "sha256": digest(item), "size": item.stat().st_size, "host": item}
            elif entry["type"] == "l":
                live_tree[path] = {"type": "l", "target": entry["target"]}
        live_files = {path: live_tree[path] for path, entry in live.items() if entry["type"] in ("-", "l")}
        add = sorted(set(live_files) - set(stock_files))
        delete = sorted(set(stock_files) - set(live_files))
        replace = sorted(path for path in set(live_files) & set(stock_files)
                         if live_files[path]["type"] != stock_files[path]["type"] or
                         (live_files[path]["type"] == "-" and live_files[path]["sha256"] != stock_files[path].get("sha256")) or
                         (live_files[path]["type"] == "l" and live_files[path]["target"] != stock_files[path].get("target")))
        changed = sorted(set(add) | set(replace))
        for path in changed:
            if live_files[path]["type"] == "-" and not Path(live_files[path]["host"]).is_file():
                raise ValueError(f"No local file contents for changed path: {path}")
        apk_sha = digest(apk)
        validate_apk(apk, aapt2)
        bootanimation_sha = None
        if bootanimation is not None:
            validate_bootanimation(bootanimation)
            bootanimation_sha = digest(bootanimation)
            if live.get("/media/bootanimation.zip", {}).get("type") != "-":
                raise ValueError("R7A manifest lacks regular /media/bootanimation.zip")
        if "/app/FarfarRemote.apk" in stock_files or "/app/FarfarRemote.apk" in live_files:
            raise ValueError("FarfarRemote system APK path already exists; refusing to overwrite")

        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="e2003-r7a-poc-", dir=output.parent) as temp_name:
            work = Path(temp_name)
            temp_image = work / "system.ext4"
            shutil.copyfile(source, temp_image)
            payloads: dict[str, Path] = {}
            for index, path in enumerate(changed):
                if live_files[path]["type"] == "-":
                    staged = work / f"payload-{index:04d}"
                    shutil.copyfile(Path(live_files[path]["host"]), staged)
                    payloads[path] = staged
            apk_stage = work / "FarfarRemote.apk"
            shutil.copyfile(apk, apk_stage)
            boot_stage = work / "bootanimation.zip" if bootanimation is not None else None
            if bootanimation is not None:
                shutil.copyfile(bootanimation, boot_stage)

            # Confirm that every source-tree payload being removed/replaced is
            # actually present byte-for-byte in the pinned R10A ext4 input.
            old_paths = [path for path in sorted(set(delete) | set(replace))
                         if stock_files.get(path, {}).get("type") == "-"]
            old_dump = {}
            source_checks = []
            for index, path in enumerate(old_paths):
                destination = work / f"source-check-{index:04d}"
                source_checks.append(f"dump {path} {destination}")
                old_dump[path] = destination
            if source_checks:
                read_debugfs(source, source_checks, work)
                for path, extracted in old_dump.items():
                    if digest(extracted) != stock_files[path]["sha256"]:
                        raise ValueError(f"R10A extracted-tree file does not match source image: {path}")

            commands: list[str] = []
            # Create missing live directories parent-first.
            for directory in sorted(live_dirs - stock_dirs, key=lambda p: (p.count("/"), p)):
                if directory != "/": commands.append(f"mkdir {directory}")
            # Remove candidate-only content and content/type replacements.
            for path in sorted(set(delete) | set(replace), key=lambda p: (-p.count("/"), p)):
                commands.append(f"rm {path}")
            # Add or replace live file payloads.
            for path in changed:
                entry = live_files[path]
                if entry["type"] == "-":
                    commands.append(f"write {payloads[path]} {path}")
                else:
                    commands.append(f"symlink {path} {entry['target']}")
            # Remove now-empty directories that exist only in R10A.
            for directory in sorted(stock_dirs - live_dirs, key=lambda p: (-p.count("/"), p)):
                if directory != "/": commands.append(f"rmdir {directory}")
            # Preserve metadata for unchanged inodes. A read-only stat comparison
            # against this hash-pinned source found only these two label deltas.
            # Apply full metadata only to newly created/replaced entries.
            metadata_paths = set(changed) | (live_dirs - stock_dirs)
            label_repairs = {
                "/bin/6620_wmt_concurrency",
                "/bin/audiocmdservice_atci",
            }
            for path in sorted(metadata_paths, key=lambda p: (p.count("/"), p)):
                entry = live[path]
                inode_mode = {"-": 0o100000, "d": 0o040000, "l": 0o120000}.get(entry["type"], 0)
                if not inode_mode:
                    raise ValueError(f"Unsupported inode type at {path}: {entry['type']}")
                mode = inode_mode | int(entry["mode"])
                commands.extend((f"sif {path} uid {entry['uid']}", f"sif {path} gid {entry['gid']}",
                                 f"sif {path} mode {mode:07o}",
                                 f"ea_set {path} security.selinux {entry['label']}"))
            for path in sorted(label_repairs):
                if path not in live or path in metadata_paths:
                    continue
                commands.append(f"ea_set {path} security.selinux {live[path]['label']}")
            commands.append(f"write {apk_stage} /app/FarfarRemote.apk")
            commands.extend(("sif /app/FarfarRemote.apk uid 0", "sif /app/FarfarRemote.apk gid 0",
                             "sif /app/FarfarRemote.apk mode 0100644",
                             "ea_set /app/FarfarRemote.apk security.selinux u:object_r:system_file:s0"))
            if boot_stage is not None:
                boot_entry = live["/media/bootanimation.zip"]
                commands.extend(("rm /media/bootanimation.zip",
                                 f"write {boot_stage} /media/bootanimation.zip",
                                 f"sif /media/bootanimation.zip uid {boot_entry['uid']}",
                                 f"sif /media/bootanimation.zip gid {boot_entry['gid']}",
                                 f"sif /media/bootanimation.zip mode {0o100000 | int(boot_entry['mode']):07o}",
                                 f"ea_set /media/bootanimation.zip security.selinux {boot_entry['label']}"))
            run_debugfs(temp_image, commands, work)

            # Verify changed/deleted file operations by readback before publishing output.
            verify: list[str] = []
            expected: dict[str, Path] = {}
            for index, path in enumerate(changed):
                if live_files[path]["type"] == "-":
                    destination = work / f"readback-{index:04d}"
                    verify.append(f"dump {path} {destination}")
                    expected[path] = destination
            apk_readback = work / "apk-readback.apk"
            verify.append(f"dump /app/FarfarRemote.apk {apk_readback}")
            boot_readback = work / "bootanimation-readback.zip"
            if boot_stage is not None:
                verify.append(f"dump /media/bootanimation.zip {boot_readback}")
            run_debugfs(temp_image, verify, work)
            for path in expected:
                if digest(expected[path]) != digest(Path(live_files[path]["host"])):
                    raise RuntimeError(f"Readback hash mismatch after update: {path}")
            if digest(apk_readback) != apk_sha:
                raise RuntimeError("FarfarRemote APK readback hash mismatch")
            if boot_stage is not None and digest(boot_readback) != bootanimation_sha:
                raise RuntimeError("bootanimation ZIP readback hash mismatch")
            for path in delete:
                check = subprocess.run(["debugfs", "-R", f"stat {path}", str(temp_image)],
                                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if "File not found" not in (check.stdout + check.stderr):
                    raise RuntimeError(f"Candidate-only path remains after removal: {path}")

            fsck = subprocess.run(["e2fsck", "-fn", str(temp_image)], text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if fsck.returncode != 0:
                raise RuntimeError(f"e2fsck failed with exit {fsck.returncode}: {fsck.stdout[-2000:]}")
            temp_image.replace(output)
        print(f"output={output}")
        print(f"output_sha256={digest(output)}")
        print(f"source_sha256={SOURCE_SHA256}")
        print(f"apk_sha256={apk_sha}")
        if bootanimation_sha:
            print(f"bootanimation_sha256={bootanimation_sha}")
        print(f"r7a_files_added={len(add)} r10a_only_files_removed={len(delete)} files_replaced={len(replace)}")
        print("e2fsck passed; this is an offline ext4 POC, not a flashable/boot-tested firmware image")
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
