#!/usr/bin/env python3
"""Dependency-free contract guard for protected behavior and distribution manifests."""

from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
# Freeze the last full implementation checkpoint. Earlier v0.2 comparisons became
# invalid when later Kodi folder browsing and active-stream path support were added.
BASE = "b71fbef"
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
check(new_client == old_client, "KodiClient unchanged from the release implementation checkpoint")
header = method_block(new_main, "addHeader")
check('new SpannableString("FarfarRemote")' in header and "new ForegroundColorSpan(CYAN)" in header,
      "FarfarRemote wordmark uses one text view with cyan accent span")
check("brand.setSingleLine(true)" in header and 'hostLabel.setMaxWidth(dp(120))' in header and 'status.setMaxWidth(dp(120))' in header,
      "wordmark and connection labels are constrained to a single compact header row")
check('setStatus(connected ? "CONNECTED" : "Kodi offline · Settings to configure")' not in new_main,
      "startup uses the compact offline header state")

protected_methods = (
    "applyOrientationPreference",
    "addDpad", "presentTracks", "chooseStream", "back", "playPause",
    "stop", "seekStep", "goTo", "seekPercent", "activate", "adjustVolume",
    "toggleMute", "client", "applySnapshot",
)
for name in protected_methods:
    check(method_block(new_main, name) == method_block(old_main, name), f"{name} unchanged from the release implementation checkpoint")

check(method_block(new_main, "showStreams") == method_block(old_main, "showStreams"),
      "Audio/Subtitles stream selection unchanged from the release implementation checkpoint")
check(method_block(new_main, "action") == method_block(old_main, "action"),
      "Kodi action payloads and UI results unchanged from the release implementation checkpoint")

for name in ("buildPortrait", "buildLandscape"):
    check(method_block(new_main, name) == method_block(old_main, name),
          f"{name} unchanged from the release implementation checkpoint")

build = (ROOT / "app/build.gradle").read_text()
check("applicationId 'org.farfarremote'" in build, "OS applicationId retained")
check("compileSdk 36" in build and "minSdk 19" in build and "versionCode 15" in build and "versionName '0.4.7'" in build, "compile SDK 36, min SDK 19, and v0.4.7 stable metadata")
check(re.search(r"app \{(?:(?!\n\s*\}).)*targetSdk 36", build, re.S) is not None, "App flavor targets API 36")
check(re.search(r"os \{(?:(?!\n\s*\}).)*targetSdk 28", build, re.S) is not None, "OS flavor retains conservative API 28 target")
app_manifest = ET.parse(ROOT / "app/src/app/AndroidManifest.xml").getroot()
os_manifest = ET.parse(ROOT / "app/src/os/AndroidManifest.xml").getroot()
def categories_in(overlay):
    return {node.attrib.get(f"{{{ANDROID}}}name") for node in overlay.findall(".//intent-filter/category")}
check("android.intent.category.LAUNCHER" in categories_in(app_manifest), "App flavor has normal launcher icon")
check("android.intent.category.HOME" not in categories_in(app_manifest), "App flavor does not claim HOME")
check("android.intent.category.HOME" in categories_in(os_manifest) and "android.intent.category.DEFAULT" in categories_in(os_manifest), "OS flavor retains HOME launcher intent")
check(app_manifest.find("application").attrib.get(f"{{{ANDROID}}}enableOnBackInvokedCallback") == "true", "App flavor opts into modern predictive back handling")

for key in ("host", "port", "user", "pass", "orientation", "keep_awake", "auto_reconnect", "haptics"):
    check(f'"{key}"' in new_main, f"preference key {key} retained")

check(new_main.count('prefs.getBoolean("keep_awake", false)') == 2,
      "screen-awake preference defaults off in behavior and Settings UI")
check("FLAG_KEEP_SCREEN_ON" in new_main and "clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)" in new_main,
      "Keep Screen Awake remains an explicit opt-in override")

check('https://buymeacoffee.com/farfarspelar' in new_main and "Intent.ACTION_VIEW" in new_main, "support link uses requested external ACTION_VIEW URL")
check("ClipboardManager" in new_main and "ActivityNotFoundException" in new_main, "no-browser clipboard fallback present")
check("NsdManager" in new_main and '"_xbmc-jsonrpc-h._tcp."' in new_main, "Find My Kodi uses Kodi HTTP JSON-RPC DNS-SD only")
check("Kodi did not respond" in new_main and "Use and Save" in new_main, "Kodi candidates are JSON-RPC checked and require confirmation")
check('call("System.Shutdown", new JSONObject())' in new_main and 'Power off Kodi?' in new_main,
      "Power Off requires confirmation and calls Kodi System.Shutdown")
check("The Android remote will stay on." in new_main, "Power Off confirmation distinguishes Kodi host from Android remote")
check("addPowerControl(header, power, 31)" in new_main, "Power Off occupies the header control position")
check("stopKodiDiscovery(true)" in new_main and "KODI_DISCOVERY_TIMEOUT_MS" in new_main, "discovery has timeout and lifecycle cleanup")
check("activityStarted;" in new_main and "long next = isDedicatedOs() ? osPollDelayMs(result) : 2800" in new_main,
      "OS battery policy is flavor-gated and App retains its 2.8-second foreground poll")
check("@Override protected void onStart()" in new_main and "handler.removeCallbacks(poll)" in new_main, "poll loop starts without duplicate callbacks")
check("@Override protected void onStop()" in new_main and "activityStarted = false; handler.removeCallbacks(poll)" in new_main, "polling stops when the activity is backgrounded")
check("setShowText(" not in new_main, "no Switch API 21 setShowText call on API 19")
check("Build.VERSION.SDK_INT < 35" in new_main and "Api35WindowInsets.install(target)" in new_main, "App insets are API-gated; API 19 remains supported")
check("Api33BackHandler.register(this, this::closeOverlay)" in new_main, "App Settings and library use modern platform Back callback")
check('android:usesCleartextTraffic="true"' in (ROOT / "app/src/main/AndroidManifest.xml").read_text(), "Kodi HTTP connectivity remains enabled")
check((ROOT / "app/src/main/res/drawable/settings_input_background.xml").is_file(), "focus-state input selector exists")
check((ROOT / "app/src/main/res/drawable/settings_orientation_background.xml").is_file(), "selected orientation selector exists")
print("All FarfarRemote v0.4.7 distribution and regression contract checks passed.")
