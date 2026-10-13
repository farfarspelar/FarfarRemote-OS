#!/usr/bin/env python3
"""Compare read-only metric snapshots collected by debloat.sh."""
import argparse
import re
from pathlib import Path

def oom(path):
    text=(path/"memory.txt").read_text(errors="replace")
    out={}; block=re.search(r"Total PSS by OOM adjustment:\n(.*?)(?=\nTotal PSS by category:)",text,re.S)
    if block:
        current=""
        for line in block.group(1).splitlines():
            head=re.match(r"^\s{3,}([\d,]+) kB: ([A-Za-z ]+)$",line)
            item=re.match(r"^\s+([\d,]+) kB: (\S+)",line)
            if head:
                current=head.group(2).strip(); out[current]=int(head.group(1).replace(",",""))
    ram=(path/"memory.txt").read_text(errors="replace")
    def value(label):
        # Android 4.4 dumpsys meminfo indents Free/Used RAM, unlike Total RAM.
        m=re.search(rf"^\s*{re.escape(label)}:\s*([\d,]+) kB",ram,re.M)
        return int(m.group(1).replace(",","")) if m else None
    return {"total_ram":value("Total RAM"),"free_ram":value("Free RAM"),"used_ram":value("Used RAM"),"pss":out}

def cpu_counters(file):
    if not file.is_file(): return None
    for line in file.read_text(errors="replace").splitlines():
        if line.startswith("cpu "):
            vals=[int(x) for x in line.split()[1:]]
            if len(vals)>=4:
                vals += [0]*(10-len(vals))
                total=sum(vals[:8]); idle=vals[3]+vals[4]
                return total,idle
    return None

def cpu_load(path):
    a=cpu_counters(path/"proc_stat_1.txt")
    b=cpu_counters(path/"proc_stat_5.txt")
    if not a or not b: return None
    dt=b[0]-a[0]; didle=b[1]-a[1]
    if dt<=0: return None
    return 100.0*(dt-didle)/dt

def boot_times(state):
    file=state/"boot_times.tsv"; rows=[]
    if file.exists():
        for line in file.read_text(errors="replace").splitlines():
            p=line.split("\t")
            if len(p)>=3: rows.append((p[1],p[2]))
    return rows

def show(label,path):
    d=oom(path); cpu=cpu_load(path)
    kb=lambda x: f"{x:,}" if x is not None else "n/a"
    return (f"| {label} | {kb(d['free_ram'])} | {kb(d['used_ram'])} | "
            f"{kb(d['pss'].get('Cached'))} | {kb(sum(v for k,v in d['pss'].items() if k!='Cached'))} | "
            f"{cpu:.2f}%" if cpu is not None else
            f"| {label} | {kb(d['free_ram'])} | {kb(d['used_ram'])} | {kb(d['pss'].get('Cached'))} | {kb(sum(v for k,v in d['pss'].items() if k!='Cached'))} | n/a")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("state_directory",type=Path,help="reports/debloat/<adb-serial>")
    ap.add_argument("--before",help="snapshot directory name or full path")
    ap.add_argument("--after",help="snapshot directory name or full path")
    args=ap.parse_args(); state=args.state_directory.resolve(); metrics=state/"metrics"
    if not metrics.is_dir(): raise SystemExit(f"no metrics directory: {metrics}")
    snapshots=sorted(p for p in metrics.iterdir() if p.is_dir())
    if not snapshots: raise SystemExit("no metric snapshots yet")
    lines=["# FarfarRemote OS debloat metrics", "", f"Device state: `{state.name}`. Metrics are raw, read-only snapshots; no values are inferred from package count.", "",
           "`Active PSS` here is the sum of Android's non-Cached OOM buckets; `Cached PSS` is reported separately and is reclaimable. CPU is a 20-second `/proc/stat` average across the five spaced samples. Compare only after the same 5-minute idle, screen, Wi-Fi, charger and temperature conditions.", "",
           "| Snapshot | Free RAM kB | Used RAM kB | Cached PSS kB | Active PSS kB | CPU busy % |", "|---|---:|---:|---:|---:|---:|"]
    for p in snapshots: lines.append(show(p.name,p))
    if args.before and args.after:
        def resolve(x):
            q=Path(x); return q if q.is_dir() else metrics/x
        before,after=resolve(args.before),resolve(args.after)
        if not (before.is_dir() and after.is_dir()): raise SystemExit("before/after snapshot not found")
        b,a=oom(before),oom(after)
        lines += ["", f"## Change: {before.name} → {after.name}", "",
                  "| Metric | Before | After | Change |", "|---|---:|---:|---:|"]
        for key,label in [("free_ram","Free RAM"),("used_ram","Used RAM")]:
            if b[key] is not None and a[key] is not None: lines.append(f"| {label} kB | {b[key]} | {a[key]} | {a[key]-b[key]:+} |")
        for key,label in [("Cached","Cached PSS"),("Persistent","Persistent PSS"),("Foreground","Foreground PSS"),("Visible","Visible PSS"),("Perceptible","Perceptible PSS"),("A Services","A Services PSS"),("B Services","B Services PSS")]:
            bv=b['pss'].get(key); av=a['pss'].get(key)
            if bv is not None and av is not None: lines.append(f"| {label} kB | {bv} | {av} | {av-bv:+} |")
        bc,ac=cpu_load(before),cpu_load(after)
        if bc is not None and ac is not None: lines.append(f"| CPU busy % | {bc:.2f} | {ac:.2f} | {ac-bc:+.2f} percentage points |")
    boots=boot_times(state)
    lines += ["", "## Manually timed cold boots", "", "| Label | Seconds |", "|---|---:|"]
    lines += [f"| {label} | {secs} |" for label,secs in boots] or ["| No stopwatch results recorded | — |"]
    lines += ["", "Cold boot time is recorded manually because the supplied audit has no paired kernel-start and HOME-ready event. Keep run conditions comparable. No automatic performance improvement claim is made until a before/after pair exists.", ""]
    out=state/"metrics_review.md"; out.write_text("\n".join(lines),encoding="utf-8"); print(out)

if __name__=="__main__": main()
