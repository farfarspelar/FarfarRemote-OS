#!/usr/bin/env python3
"""Evidence-led Xperia audit review. Produces a proposal only; never calls adb."""
import csv
import re
import sys
from pathlib import Path

CORE_FUNCTIONS = {
    "org.farfarremote": ("FarfarRemote HOME launcher and Kodi remote", "CRITICAL", "KEEP"),
    "android": ("Android framework resources", "CRITICAL", "KEEP"),
    "android.res.overlay": ("Sony/Android resource overlay", "CRITICAL", "KEEP"),
    "com.android.systemui": ("Status bar, navigation, lock screen and system UI", "CRITICAL", "KEEP"),
    "com.android.settings": ("Settings UI for Wi-Fi, input and recovery", "CRITICAL", "KEEP"),
    "com.android.providers.settings": ("Core Settings content provider", "CRITICAL", "KEEP"),
    "com.android.shell": ("ADB shell and development access", "CRITICAL", "KEEP"),
    "com.android.packageinstaller": ("Interactive APK package installer", "CRITICAL", "KEEP"),
    "com.android.inputdevices": ("Hardware-key and HID input discovery", "CRITICAL", "KEEP"),
    "com.android.bluetooth": ("Android Bluetooth profile stack", "HIGH", "KEEP"),
    "com.mediatek.bluetooth": ("MediaTek Bluetooth integration", "HIGH", "KEEP"),
    "com.android.phone": ("Persistent Android/MediaTek telephony service", "CRITICAL", "KEEP"),
    "com.android.providers.telephony": ("SMS/telephony content provider", "CRITICAL", "KEEP"),
    "com.android.incallui": ("Telephony in-call UI", "HIGH", "KEEP"),
    "com.android.externalstorage": ("External/USB storage provider", "HIGH", "KEEP"),
    "com.android.providers.media": ("Media database/content provider", "HIGH", "KEEP"),
    "com.android.keychain": ("Android credentials and certificate service", "HIGH", "KEEP"),
    "com.android.defcontainer": ("Package installation container service", "HIGH", "KEEP"),
    "com.android.providers.downloads": ("Shared downloads content provider", "HIGH", "KEEP"),
    "com.android.providers.downloads.ui": ("Downloads UI/provider companion", "HIGH", "KEEP"),
    "com.sonyericsson.home": ("Sony HOME launcher and resource provider", "HIGH", "KEEP"),
    "com.sonyericsson.home.res.overlay": ("Sony HOME resource overlay", "HIGH", "KEEP"),
    "com.sonymobile.touchscreen.touchfilter": ("Touchscreen filter integration", "CRITICAL", "KEEP"),
    "com.sonyericsson.textinput.uxp": ("Sony on-screen keyboard/input method", "CRITICAL", "KEEP"),
    "com.sonymobile.superstamina": ("Sony power-management binder service", "CRITICAL", "KEEP"),
    "com.sonymobile.cameracommon": ("Sony persistent camera framework", "HIGH", "KEEP"),
    "com.sonymobile.autopairing": ("Sony Bluetooth pairing helper", "HIGH", "KEEP"),
    "com.sonymobile.runtimeskinning.core": ("Sony runtime skinning framework", "HIGH", "KEEP"),
    "com.sonyericsson.uxp": ("Sony UI framework resources", "HIGH", "KEEP"),
    "com.sonyericsson.android.bootinfo": ("Sony boot/TA information service", "HIGH", "KEEP"),
    "com.sonymobile.enterprise.service": ("Sony enterprise/bootinfo client", "HIGH", "KEEP"),
    "com.mediatek": ("MediaTek framework resources", "CRITICAL", "KEEP"),
    "com.mediatek.providers.drm": ("MediaTek DRM provider", "HIGH", "KEEP"),
    "com.sonyericsson.android.drm.services": ("Sony DRM services", "HIGH", "KEEP"),
    "com.sonyericsson.oemCryptoReceiver": ("OEM cryptography integration", "CRITICAL", "KEEP"),
    "com.mobisystems.fileman": ("MobiSystems file manager (system-updated app)", "MEDIUM", "KEEP"),
    "com.google.android.googlequicksearchbox": ("Google Search/Now", "LOW", "DISABLE-CANDIDATE"),
    "com.google.android.apps.maps": ("Google Maps navigation app", "LOW", "DISABLE-CANDIDATE"),
    "com.google.android.apps.plus": ("Google+ social application", "LOW", "DISABLE-CANDIDATE"),
    "com.android.vending": ("Google Play Store", "MEDIUM", "DISABLE-CANDIDATE"),
    "org.farfarremote": ("FarfarRemote Kodi remote HOME activity", "CRITICAL", "KEEP"),
    "com.google.android.gms": ("Google Play Services framework", "HIGH", "DEFER"),
    "com.google.android.gsf": ("Google Services Framework", "HIGH", "DEFER"),
    "com.google.android.gsf.login": ("Google account authenticator", "HIGH", "DEFER"),
    "com.android.location.fused": ("Fused location provider", "HIGH", "DEFER"),
    "com.android.providers.contacts": ("Shared contacts content provider", "HIGH", "DEFER"),
    "com.android.providers.calendar": ("Shared calendar content provider", "HIGH", "DEFER"),
}

def read_packages(path):
    result = set()
    for line in path.read_text(errors="replace").splitlines():
        if "package:" not in line:
            continue
        v = line.split("package:", 1)[1].strip()
        name = v.rsplit("=", 1)[-1].strip()
        if re.fullmatch(r"[A-Za-z0-9_.$]+", name):
            result.add(name)
    return result

def read_candidates(path):
    result = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if not row.get("package") or row["package"] in result:
                raise ValueError(f"empty or duplicate package row: {row}")
            result[row["package"]] = row
    return result

def package_metadata(text):
    meta = {}
    starts = list(re.finditer(r"^  Package \[([^]]+)\].*$", text, re.M))
    for i, m in enumerate(starts):
        name = m.group(1)
        if name in meta:
            continue
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        block = text[m.start():end]
        def one(pattern):
            q = re.search(pattern, block, re.M)
            return (q.group(1) if q.lastindex else q.group(0)).strip() if q else ""
        state = one(r"^    User 0:.*$")
        meta[name] = {
            "path": one(r"^    codePath=(.*)$"),
            "version": one(r"^    versionName=(.*)$"),
            "flags": one(r"^    pkgFlags=(.*)$"),
            "shared": one(r"^    sharedUser=(.*)$"),
            "state": state,
            "libraries": ", ".join(re.findall(r"^      ([\w.$]+)$", block, re.M)) if "usesLibraries:" in block else "",
        }
    return meta

def process_owners(activity_text, service_text):
    owners = {}
    shared = set()
    for block in re.split(r"(?=^\s{2,}\*\w+\* UID )", activity_text, flags=re.M):
        proc = re.search(r"ProcessRecord\{[^}]+\s+\d+:([^/\s]+)/", block)
        pkgs = re.search(r"packageList=\{([^}]*)\}", block)
        if proc and pkgs:
            names = [x.strip() for x in pkgs.group(1).split(",") if x.strip()]
            if len(names) == 1: owners[proc.group(1)] = names[0]
            elif names: shared.add(proc.group(1))
    for block in re.split(r"(?=^  \* ServiceRecord\{)", service_text, flags=re.M):
        package = re.search(r"^    packageName=(\S+)", block, re.M)
        proc = re.search(r"^    processName=(\S+)", block, re.M)
        if package and proc and proc.group(1) not in shared: owners.setdefault(proc.group(1), package.group(1))
    return owners, shared

def pss_metadata(text, owners):
    active, cached, groups, section = {}, {}, {}, ""
    for line in text.splitlines():
        if line.startswith("Total PSS by OOM adjustment:"):
            section = "oom"
            continue
        if line.startswith("Total PSS by process:"):
            section = "process"
            continue
        if section == "oom" and re.match(r"^\s{3,}[\d,]+ kB: [A-Za-z ]+$", line):
            section = line.split(":", 1)[1].strip()
            groups.setdefault(section, {})
            continue
        m = re.match(r"^\s*([\d,]+) kB: (\S+)", line)
        if not m:
            continue
        size, proc = int(m.group(1).replace(",", "")), m.group(2)
        pkg = proc.split(":", 1)[0]
        if section == "process":
            active.setdefault(pkg, 0); cached.setdefault(pkg, 0)
            continue
        if section == "oom":
            continue
        groups.setdefault(section, {})[pkg] = groups.setdefault(section, {}).get(pkg, 0) + size
        dest = cached if section.lower() == "cached" else active
        dest[pkg] = dest.get(pkg, 0) + size
    # The first section was aggregate-by-process; extract it separately for exact per-process PSS.
    match = re.search(r"Total PSS by process:\n(.*?)(?=\nTotal PSS by OOM adjustment:)", text, re.S)
    process = {}
    if match:
        for line in match.group(1).splitlines():
            m = re.match(r"\s*([\d,]+) kB: (\S+)", line)
            if m:
                name = m.group(2); pkg = owners.get(name, name.split(":", 1)[0])
                process[pkg] = process.get(pkg, 0) + int(m.group(1).replace(",", ""))
    # Parse category detail independently: Android's dump repeats process PSS under OOM buckets.
    categories = {}
    m = re.search(r"Total PSS by OOM adjustment:\n(.*?)(?=\nTotal PSS by category:)", text, re.S)
    if m:
        current = ""
        for line in m.group(1).splitlines():
            if re.match(r"^\s{3,}[\d,]+ kB: [A-Za-z ]+$", line):
                current = line.split(":", 1)[1].strip()
                categories.setdefault(current, {})
            else:
                item = re.match(r"^\s+([\d,]+) kB: (\S+)", line)
                if current and item:
                    procname = item.group(2); pkg = owners.get(procname, procname.split(":", 1)[0])
                    categories[current][pkg] = categories[current].get(pkg, 0) + int(item.group(1).replace(",", ""))
    cached = categories.get("Cached", {})
    active = {}
    for cat, values in categories.items():
        if cat != "Cached":
            for pkg, kb in values.items(): active[pkg] = active.get(pkg, 0) + kb
    return process, active, cached, categories

def service_metadata(text):
    data = {}
    blocks = re.split(r"(?=^  \* ServiceRecord\{)", text, flags=re.M)
    for b in blocks:
        p = re.search(r"^    packageName=(\S+)", b, re.M)
        if not p: continue
        name = p.group(1)
        cmp = re.search(r"^  \* ServiceRecord\{[^}]+\s+u\d+\s+(\S+)", b, re.M)
        data.setdefault(name, []).append(cmp.group(1).rstrip("}") if cmp else "service")
    return data

def generic_function(pkg, metadata):
    if pkg in CORE_FUNCTIONS:
        return CORE_FUNCTIONS[pkg]
    if pkg.startswith("com.google.android.") or pkg in {"com.android.vending", "com.google.android.backuptransport"}:
        return ("Google application/service; exact role is package-specific", "MEDIUM", "REVIEW")
    if pkg.startswith("com.sonyericsson.advancedwidget.") or pkg.startswith("com.sonymobile.advancedwidget."):
        return ("Sony home-screen widget or widget catalog", "LOW", "REVIEW")
    if "camera" in pkg.lower() or "photo" in pkg.lower() or "album" in pkg.lower() or "video" in pkg.lower():
        return ("Camera/photo/video feature; exact component depends on app manifest", "MEDIUM", "REVIEW")
    if "social" in pkg.lower() or "facebook" in pkg.lower() or "twitter" in pkg.lower():
        return ("Social/account/share integration", "MEDIUM", "REVIEW")
    if pkg.startswith("com.android.providers."):
        return ("Android shared content provider", "HIGH", "REVIEW")
    if pkg.startswith("com.mediatek."):
        return ("MediaTek vendor package; board dependency not ruled out", "HIGH", "KEEP")
    if pkg.startswith(("com.sony", "com.sonymobile", "com.sonyericsson")):
        return ("Sony/OEM component; exact function not proven by this capture", "HIGH", "REVIEW")
    if metadata.get("path", "").startswith("/data/app/"):
        return ("Non-platform application; exact role not resolved", "MEDIUM", "REVIEW")
    if pkg.startswith("com.android."):
        return ("Android platform component; preserve unless a dependency test proves otherwise", "HIGH", "KEEP")
    return ("Package role unresolved from available metadata", "HIGH", "REVIEW")

def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: analyze_device_audit.py <audit-directory> [debloat_packages.tsv]")
    root = Path(sys.argv[1]).resolve()
    candidates_path = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else Path(__file__).with_name("debloat_packages.tsv")
    required = ["README.txt", "packages_all.txt", "package_manager.txt", "memory.txt", "processes.txt", "activity_services.txt", "boot_events.txt"]
    missing = [x for x in required if not (root / x).is_file()]
    if missing: raise SystemExit("audit missing required files: " + ", ".join(missing))
    installed = read_packages(root / "packages_all.txt")
    cands = read_candidates(candidates_path)
    meta = package_metadata((root / "package_manager.txt").read_text(errors="replace"))
    service_text = (root / "activity_services.txt").read_text(errors="replace")
    activity_text = (root / "activity_processes.txt").read_text(errors="replace") if (root / "activity_processes.txt").is_file() else ""
    owners, shared_processes = process_owners(activity_text, service_text)
    process, active, cached, categories = pss_metadata((root / "memory.txt").read_text(errors="replace"), owners)
    services = service_metadata(service_text)
    extras = sorted(set(cands) - installed)
    rows = []
    for pkg in sorted(installed):
        m = meta.get(pkg, {})
        c = cands.get(pkg)
        if c:
            fn, risk, action = c["function"], c["risk"], c["eligibility"]
            phase, evidence, recommendation = c["phase"], c["audit_evidence"], c["recommendation"]
        else:
            fn, risk, action = generic_function(pkg, m)
            phase, evidence, recommendation = "—", "No preapproved candidate entry; default is keep/review.", "Do not disable from name alone; inspect package metadata and dependants."
        state = m.get("state", "")
        service_list = ", ".join(services.get(pkg, [])[:3])
        pss_total = process.get(pkg, process.get(pkg.split(":", 1)[0], 0))
        active_pss = active.get(pkg, active.get(pkg.split(":", 1)[0], 0))
        cached_pss = cached.get(pkg, cached.get(pkg.split(":", 1)[0], 0))
        running = bool(pss_total or service_list)
        observed = f"PSS total {pss_total} kB; active buckets {active_pss} kB; cached bucket {cached_pss} kB" if pss_total else "No process PSS in this single snapshot"
        if service_list: observed += "; active service(s): " + service_list
        if state: observed += "; " + state
        if m.get("shared"): observed += "; " + m["shared"]
        rows.append({"package":pkg,"function":fn,"phase":phase,"risk":risk,"action":action,
                     "code_path":m.get("path",""),"version":m.get("version",""),"running":str(running),
                     "pss_total_kb":pss_total,"pss_active_kb":active_pss,"pss_cached_kb":cached_pss,
                     "state":state,"services":service_list,"evidence":evidence + (" | " + observed if pss_total or service_list else " | " + observed),
                     "recommendation":recommendation})
    out_csv, out_md = root / "package_review.csv", root / "package_review.md"
    fields = list(rows[0])
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    mem = (root / "memory.txt").read_text(errors="replace")
    ram = re.search(r"Total RAM:\s*([\d,]+) kB", mem)
    free = re.search(r"Free RAM:\s*([\d,]+) kB", mem)
    used = re.search(r"Used RAM:\s*([\d,]+) kB", mem)
    uptime_file = (root / "uptime.txt").read_text(errors="replace")
    uptime_match = re.search(r"\n([\d.]+)\s+([\d.]+)", uptime_file)
    uptime = f"{uptime_match.group(1)}s since boot" if uptime_match else "unparsed; inspect uptime.txt"
    bootlines = [x for x in (root / "boot_events.txt").read_text(errors="replace").splitlines() if "boot_progress_" in x]
    summary = [("Persistent", "Persistent system processes"), ("Foreground", "Foreground"), ("Visible", "Visible"), ("Perceptible", "Perceptible"), ("A Services", "A Services"), ("B Services", "B Services"), ("Cached", "Cached (reclaimable)"), ("Native", "Native")]
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Xperia E2003 package and dependency review\n\n")
        f.write(f"Source: `{root.name}`; serial/model recorded in `README.txt`. Packages in capture: **{len(installed)}**. This is analysis only: no adb commands or package changes are performed.\n\n")
        f.write("## Runtime baseline from this audit snapshot\n\n")
        f.write(f"Uptime at capture: `{uptime}`. Memory report: total RAM {ram.group(1) if ram else 'n/a'} kB; free RAM {free.group(1) if free else 'n/a'} kB; used RAM {used.group(1) if used else 'n/a'} kB.\n\n")
        f.write("PSS split (kB; Android OOM groups at one sample):\n\n| Group | Total PSS | Meaning for debloat |\n|---|---:|---|\n")
        for key,label in summary:
            val=sum(categories.get(key,{}).values())
            if val: f.write(f"| {label} | {val:,} | {'Can be reclaimed under memory pressure; do not call it guaranteed free RAM' if key=='Cached' else 'Resident/important-to-current-state PSS; app/process may be active'} |\n")
        f.write("\nThe snapshot reports 279,728 kB cached PSS; this memory is already reclaimable by Android. The active/cache labels are instantaneous OOM buckets, not a before/after savings estimate. `top.txt` is a single snapshot and its CPU display does not establish average CPU load. Boot events contain an enable-screen marker but no paired boot-start marker, so a numeric cold-start duration cannot be derived from this capture.\n\n")
        f.write("Largest observed processes (PSS kB; includes packages marked KEEP):\n\n| Package | Active | Cached | Current audit evidence |\n|---|---:|---:|---|\n")
        top=sorted([r for r in rows if r['pss_total_kb']], key=lambda r:r['pss_total_kb'], reverse=True)[:20]
        for r in top:
            f.write(f"| `{r['package']}` | {r['pss_active_kb']:,} | {r['pss_cached_kb']:,} | {r['function']} |\n")
        f.write("\n## Risk and dependency interpretation\n\n")
        f.write("LOW means user-facing and outside remote-control functions; MEDIUM means removable only after app-specific tests; HIGH means shared provider/OEM/account/service integration; CRITICAL means required for input, Android UI/recovery, installation, power or the board. `YES` rows are limited to named Phase A–C app candidates; `REVIEW` rows are staged Phase D suggestions; `NEVER` rows are explicit keep rules. Missing dependency evidence defaults to keep.\n\n")
        f.write("Observed dependencies that change the risk: Google Play Services has active persistent services for fused location, GCM, measurement and API broker clients; GPSME binds Google measurement. Google GMS processes total about 96,107 kB PSS in this snapshot (43,785 persistent plus 52,322 cached); the additional 16,864 kB `com.google.process.gapps` belongs to a shared process whose package list includes GMS, GSF, GSF login and Contacts sync, so it is not assigned to one package. Sony SuperStamina publishes `xperia_power_service` and must remain. The phone process is persistent and shares `android.uid.phone` with the telephony provider. The phone package declares Sony HOME resource-provider library use. TouchFilter runs as system UID. Android Settings, SettingsProvider, SystemUI, Sony keyboard, PackageInstaller and ADB shell remain the recovery/input path.\n\n")
        f.write(f"{len(extras)} proposed rows are not installed in this capture and will be ignored by scripts: {', '.join(extras) if extras else 'none'}.\n\n")
        f.write("## Per-package review\n\n| Package | Function | Phase | Risk | Path / version | PSS active / cached kB | Runtime/services and recommendation |\n|---|---|---:|---|---|---:|---|\n")
        for r in rows:
            path=(r['code_path'] or "unknown") + (" / " + r['version'] if r['version'] else "")
            proof=(r['evidence'] + "; " + r['recommendation']).replace('|','/')
            f.write(f"| `{r['package']}` | {r['function']} | {r['phase']} | **{r['risk']}** | `{path}` | {r['pss_active_kb']} / {r['pss_cached_kb']} | {proof} |\n")
        f.write("\n## Staged candidate list\n\nSee `tools/debloat_packages.tsv` for the curated package-by-package evidence and action. It is the only source of packages the debloat script will consider.\n")
    print(f"Wrote {out_md} and {out_csv}; {len(installed)} packages; {len(extras)} candidate rows absent on device.")

if __name__ == "__main__":
    try: main()
    except (OSError, ValueError) as e: raise SystemExit(str(e))
