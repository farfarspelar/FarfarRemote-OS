#!/usr/bin/env python3
"""Compare two unplugged FarfarRemote battery sessions without endurance extrapolation."""
import argparse
import csv
import pathlib
import sys


def read_session(path: pathlib.Path):
    session = path / "session.txt"
    samples = path / "samples.csv"
    if not session.is_file() or not samples.is_file():
        raise ValueError(f"not a battery session directory: {path}")
    meta = {}
    for line in session.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1); meta[k] = v
    with samples.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 2:
        raise ValueError(f"session has fewer than two samples: {path}")
    if any(x.get("usb_powered") == "true" or x.get("ac_powered") == "true" for x in rows):
        raise ValueError(f"charging detected in session: {path}")
    return meta, rows


def summarize(meta, rows):
    start, end = rows[0], rows[-1]
    elapsed = float(end["monotonic"]) - float(start["monotonic"])
    delta_level = float(end["level_pct"]) - float(start["level_pct"])
    t0, t1 = int(start["cpu_total_ticks"]), int(end["cpu_total_ticks"])
    i0, i1 = int(start["cpu_idle_ticks"]), int(end["cpu_idle_ticks"])
    cpu_busy = 100.0 * ((t1 - t0) - (i1 - i0)) / (t1 - t0) if t1 > t0 else None
    polls = None
    session_path = pathlib.Path(meta.get("_path", "."))
    start_log, end_log = session_path / "battery_poll_log_start.txt", session_path / "battery_poll_log_end.txt"
    if end_log.is_file():
        def poll_lines(path):
            if not path.is_file(): return set()
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            if any(line.startswith("Unavailable:") for line in lines): return None
            return {line for line in lines if "poll_start" in line}
        end_polls = poll_lines(end_log)
        start_polls = poll_lines(start_log)
        if end_polls is not None and start_polls is not None:
            polls = len(end_polls - start_polls)
    return {
        "label": meta.get("label", "unknown"), "scenario": meta.get("scenario", "unknown"),
        "elapsed": elapsed, "level_start": start["level_pct"], "level_end": end["level_pct"],
        "delta_level": delta_level, "voltage_start": start["voltage_mv"], "voltage_end": end["voltage_mv"],
        "temp_start": start["temperature_tenths_c"], "temp_end": end["temperature_tenths_c"],
        "cpu_busy": cpu_busy, "screen_start": start["screen_on"], "screen_end": end["screen_on"], "polls": polls,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("baseline", type=pathlib.Path)
    ap.add_argument("optimized", type=pathlib.Path)
    args = ap.parse_args()
    try:
        bm, br = read_session(args.baseline); om, ore = read_session(args.optimized)
        if bm.get("scenario") != om.get("scenario"):
            raise ValueError("scenarios differ; compare matching scenarios only")
        b = summarize({**bm, "_path": str(args.baseline)}, br)
        o = summarize({**om, "_path": str(args.optimized)}, ore)
        print(f"Scenario: {b['scenario']}")
        for title, x in (("Baseline", b), ("Optimized", o)):
            cpu = "unavailable" if x["cpu_busy"] is None else f"{x['cpu_busy']:.1f}% aggregate CPU busy ticks"
            polls = "not logged" if x["polls"] is None else f"{x['polls']} poll starts visible in end log buffer (lower-bound only)"
            print(f"{title} ({x['label']}): actual {x['elapsed']:.0f}s; battery {x['level_start']}% → {x['level_end']}% ({x['delta_level']:+.1f} percentage points); voltage {x['voltage_start']} → {x['voltage_end']} mV; temperature {x['temp_start']} → {x['temp_end']} tenths °C; screen {x['screen_start']} → {x['screen_end']}; {cpu}; {polls}.")
        print("No battery endurance projection is calculated. Small sessions may show no level change because Android reports integer percentages.")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"compare_battery_sessions: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
