#!/usr/bin/env python3
"""Small dependency-free guard for the v0.3 Settings-only change set."""

from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "a840155"
MAIN = "app/src/main/java/org/farfarremote/MainActivity.java"
ANDROID = "http://schemas.android.com/apk/res/android"


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def method_block(source, name):
    pattern = re.compile(
        rf"(?m)^\s*(?:private|protected|public)\s+[^;{{}}\n]+\b{re.escape(name)}\s*\([^;{{}}]*\)\s*(?:throws\s+[^{{]+)?\{{"
    )
    match = pattern.search(source)
    if not match:
        fail(f"could not find method {name}")
    start = match.start()
    opening = source.find("{", match.start(), match.end())
    depth = 0
    state = "code"
    i = opening
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if state == "code":
            if ch == '"': state = "string"
            elif ch == "'": state = "char"
            elif ch == "/" and nxt == "/": state = "line"
            elif ch == "/" and nxt == "*": state = "block"; i += 1
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0: return source[start:i + 1]
        elif state == "string":
            if ch == "\\": i += 1
            elif ch == '"': state = "code"
        elif state == "char":
            if ch == "\\": i += 1
            elif ch == "'": state = "code"
        elif state == "line":
            if ch == "\n": state = "code"
        elif state == "block" and ch == "*" and nxt == "/":
            state = "code"; i += 1
        i += 1
    fail(f"unbalanced method {name}")


def git_show(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True)


def check(condition, label):
    if not condition: fail(label)
    print(f"PASS: {label}")


try:
    old_main = git_show(MAIN)
    old_client = git_show("app/src/main/java/org/farfarremote/KodiClient.java")
except subprocess.CalledProcessError:
    fail(f"baseline commit {BASE} is unavailable; run this inside the full repository history")

new_main = (ROOT / MAIN).read_text()
new_client = (ROOT / "app/src/main/java/org/farfarremote/KodiClient.java").read_text()
check(new_client == old_client, "KodiClient byte-for-byte unchanged from v0.2 baseline")

protected_methods = (
    "applyOrientationPreference", "applyKeepAwake", "buildPortrait", "buildLandscape",
    "addDpad", "showStreams", "presentTracks", "chooseStream", "back", "playPause",
    "stop", "seekStep", "goTo", "seekPercent", "activate", "adjustVolume",
    "toggleMute", "action", "client", "applySnapshot",
)
for name in protected_methods:
    check(method_block(new_main, name) == method_block(old_main, name), f"{name} unchanged from v0.2")

manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
application = manifest.find("application")
activity = application.find("activity")
categories = {node.attrib.get(f"{{{ANDROID}}}name") for node in activity.findall("intent-filter/category")}
build = (ROOT / "app/build.gradle").read_text()
check("applicationId 'org.farfarremote'" in build, "applicationId retained")
check("minSdk 19" in build and "versionCode 3" in build and "versionName '0.3.0'" in build, "API 19 and v0.3 version metadata")
check("android.intent.category.HOME" in categories and "android.intent.category.DEFAULT" in categories, "HOME launcher intent retained")

for key in ("host", "port", "user", "pass", "orientation", "keep_awake", "auto_reconnect", "haptics"):
    check(f'"{key}"' in new_main, f"preference key {key} retained")

check('https://buymeacoffee.com/farfarspelar' in new_main and "Intent.ACTION_VIEW" in new_main, "support link uses requested external ACTION_VIEW URL")
check("ClipboardManager" in new_main and "ActivityNotFoundException" in new_main, "no-browser clipboard fallback present")
check("setShowText(" not in new_main, "no Switch API 21 setShowText call on API 19")
check((ROOT / "app/src/main/res/drawable/settings_input_background.xml").is_file(), "focus-state input selector exists")
check((ROOT / "app/src/main/res/drawable/settings_orientation_background.xml").is_file(), "selected orientation selector exists")
print("All v0.3 Settings contract checks passed.")
