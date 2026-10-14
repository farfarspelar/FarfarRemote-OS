#!/usr/bin/env python3
"""Capture a read-only, unplugged E2003 battery session through ADB."""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENARIOS = (
    "screen_off_idle", "screen_on_idle", "kodi_connected_idle",
    "kodi_playback", "kodi_disconnected", "intermittent_use",
)


def run(adb: str, serial: str, *args: str, timeout: int = 40) -> str:
    p = subprocess.run([adb, "-s", serial, *args], text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"adb {' '.join(args[:2])} failed: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.replace("\r", "")


def one_value(text: str, key: str) -> str:
    m = re.search(r"^\s*" + re.escape(key) + r":\s*(.*?)\s*$", text, re.M | re.I)
    return m.group(1) if m else "unknown"


def parse_proc_stat(text: str) -> tuple[int, int]:
    line = next((x for x in text.splitlines() if x.startswith("cpu ")), "")
    vals = [int(x) for x in line.split()[1:]]
    if len(vals) < 4:
        return 0, 0
    total = sum(vals)
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    return total, idle


def device_serial(adb: str) -> tuple[str, str]:
    p = subprocess.run([adb, "devices", "-l"], text=True, capture_output=True)
    devices = [line for line in p.stdout.splitlines()[1:] if re.search(r"\sdevice(?:\s|$)", line)]
    if len(devices) != 1:
        raise RuntimeError(f"Expected exactly one authorized ADB device, found {len(devices)}.")
    fields = devices[0].split()
    serial = fields[0]
    props = subprocess.run([adb, "-s", serial, "shell", "getprop", "ro.product.model"], text=True, capture_output=True).stdout.strip()
    product = subprocess.run([adb, "-s", serial, "shell", "getprop", "ro.build.product"], text=True, capture_output=True).stdout.strip()
    if "E2003" not in props and "E2003" not in product:
        raise RuntimeError(f"Device is not identified as Xperia E2003 (model={props!r}, product={product!r}).")
    return serial, devices[0]


def snapshot(adb: str, serial: str) -> dict[str, object]:
    battery = run(adb, serial, "shell", "dumpsys", "battery")
    if re.search(r"^\s*(?:AC|USB|Wireless) powered:\s*true\s*$", battery, re.M | re.I):
        raise RuntimeError("Charging is active. Battery-endurance runs must be unplugged; use wireless ADB or capture after disconnecting USB.")
    power = run(adb, serial, "shell", "dumpsys", "power")
    proc = run(adb, serial, "shell", "cat", "/proc/stat")
    uptime_text = run(adb, serial, "shell", "cat", "/proc/uptime")
    uptime = uptime_text.split()[0] if uptime_text.split() else "unknown"
    screen_matches = re.findall(r"mScreenOn=(true|false)", power, re.I)
    screen = screen_matches[-1].lower() if screen_matches else "unknown"
    status_code = one_value(battery, "status")
    status_label = {"1": "unknown", "2": "charging", "3": "discharging", "4": "not_charging", "5": "full"}.get(status_code, "unknown")
    total, idle = parse_proc_stat(proc)
    return {
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "epoch": time.time(), "monotonic": time.monotonic(),
        "level_pct": one_value(battery, "level"), "voltage_mv": one_value(battery, "voltage"),
        "temperature_tenths_c": one_value(battery, "temperature"), "status": status_label, "status_code": status_code,
        "health_code": one_value(battery, "health"), "ac_powered": one_value(battery, "AC powered"),
        "usb_powered": one_value(battery, "USB powered"), "wireless_powered": one_value(battery, "Wireless powered"),
        "screen_on": screen, "uptime_seconds": uptime, "cpu_total_ticks": total, "cpu_idle_ticks": idle,
        "farfarremote_processes": sum(1 for line in run(adb, serial, "shell", "ps").splitlines() if "org.farfarremote" in line),
    }


def capture_diagnostics(adb: str, serial: str, out: pathlib.Path, phase: str) -> None:
    commands = {
        "battery": ("dumpsys", "battery"), "power": ("dumpsys", "power"),
        "wifi": ("dumpsys", "wifi"), "connectivity": ("dumpsys", "connectivity"),
        "batterystats": ("dumpsys", "batterystats"), "app_batterystats": ("dumpsys", "batterystats", "org.farfarremote"),
        "netstats": ("dumpsys", "netstats"), "processes": ("ps",),
        "top": ("top", "-n", "1", "-m", "30"),
        "battery_poll_log": ("logcat", "-d", "-v", "time", "-s", "FarfarRemoteBattery:D"),
    }
    for name, cmd in commands.items():
        try: (out / f"{name}_{phase}.txt").write_text(run(adb, serial, "shell", *cmd, timeout=90), encoding="utf-8")
        except Exception as exc: (out / f"{name}_{phase}.txt").write_text(f"Unavailable: {exc}\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label", required=True, help="e.g. baseline or balanced")
    ap.add_argument("--scenario", required=True, choices=SCENARIOS)
    ap.add_argument("--duration-seconds", type=int, default=3600)
    ap.add_argument("--interval-seconds", type=int, default=60)
    ap.add_argument("--adb", default="adb")
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", args.label):
        ap.error("label may contain only letters, digits, underscore, and hyphen")
    if args.duration_seconds < 30 or args.interval_seconds < 15:
        ap.error("duration must be at least 30 seconds and sample interval at least 15 seconds")
    try:
        serial, device_line = device_serial(args.adb)
        if re.search(r"\busb:", device_line):
            raise RuntimeError("ADB is connected over USB. Battery measurements require unplugged wireless ADB to avoid USB power invalidating the run.")
        api = run(args.adb, serial, "shell", "getprop", "ro.build.version.sdk").strip()
        release = run(args.adb, serial, "shell", "getprop", "ro.build.version.release").strip()
        if api != "19" or release != "4.4.4":
            raise RuntimeError(f"Expected Android 4.4.4/API 19; found Android {release}/API {api}.")
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = ROOT / "reports" / "os_battery" / serial / f"{stamp}_{args.label}_{args.scenario}"
        out.mkdir(parents=True, mode=0o700)
        (out / "session.txt").write_text(
            f"label={args.label}\nscenario={args.scenario}\ndevice={device_line}\nandroid={release}/API {api}\n"
            f"requested_duration_seconds={args.duration_seconds}\nsample_interval_seconds={args.interval_seconds}\n"
            "No settings were changed. USB ADB and USB/AC-powered sessions are rejected.\n",
            encoding="utf-8")
        capture_diagnostics(args.adb, serial, out, "start")
        start = snapshot(args.adb, serial)
        fields = list(start.keys())
        samples = out / "samples.csv"
        rows = [start]
        started = time.monotonic()
        deadline = started + args.duration_seconds
        with samples.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader(); writer.writerow(start); f.flush()
            while time.monotonic() < deadline:
                time.sleep(min(args.interval_seconds, max(0, deadline - time.monotonic())))
                row = snapshot(args.adb, serial)
                rows.append(row); writer.writerow(row); f.flush()
        elapsed = rows[-1]["monotonic"] - rows[0]["monotonic"]
        capture_diagnostics(args.adb, serial, out, "end")
        t0, t1 = int(rows[0]["cpu_total_ticks"]), int(rows[-1]["cpu_total_ticks"])
        i0, i1 = int(rows[0]["cpu_idle_ticks"]), int(rows[-1]["cpu_idle_ticks"])
        cpu_busy = 100.0 * ((t1 - t0) - (i1 - i0)) / (t1 - t0) if t1 > t0 else None
        start_level, end_level = rows[0]["level_pct"], rows[-1]["level_pct"]
        try: level_delta = f"{float(end_level) - float(start_level):.1f}"
        except ValueError: level_delta = "unknown"
        cpu_line = f"Aggregate CPU busy ticks: {cpu_busy:.1f}%\n" if cpu_busy is not None else "Aggregate CPU busy ticks: unavailable\n"
        summary = (
            f"Actual elapsed seconds: {elapsed:.1f}\nBattery level change (percentage points): {level_delta}\n"
            f"Start level: {start_level}%\nEnd level: {end_level}%\n{cpu_line}"
            "No endurance projection is calculated. Use matching sessions and see the measurement limits in docs/OS_BATTERY_OPTIMIZATION.md.\n"
        )
        (out / "summary.txt").write_text(summary, encoding="utf-8")
        print(f"Captured local read-only session: {out.relative_to(ROOT)}")
        print(f"Actual elapsed: {elapsed:.1f}s; battery change: {rows[0]['level_pct']}% to {rows[-1]['level_pct']}%.")
        print("No runtime estimate was extrapolated. Keep the session private; reports/os_battery is git-ignored.")
        return 0
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"battery_measure: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
