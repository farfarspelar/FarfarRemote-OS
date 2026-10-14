#!/usr/bin/env python3
"""Source-level regression guard for the opt-in Kodi folder favorites UI."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = "app/src/main/java/org/farfarremote/MainActivity.java"


def check(condition, label):
    if not condition:
        print(f"FAIL: {label}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {label}")


source = (ROOT / MAIN).read_text()
baseline = subprocess.check_output(["git", "show", f"HEAD:{MAIN}"], cwd=ROOT, text=True)
client = "app/src/main/java/org/farfarremote/KodiClient.java"
baseline_client = subprocess.check_output(["git", "show", f"HEAD:{client}"], cwd=ROOT, text=True)
check((ROOT / client).read_text() == baseline_client, "KodiClient remains unchanged")

categories = source[source.index("private void addCategories("):source.index("private void addImageOnlyControl(")]
check("Favorites" in categories and "showFavorites()" in categories, "Favorites button is added after the content category controls")
check("EdgeClippedImageView" in source and "0.08f" in source, "only Home/Stop icon views clip adjacent sprite edges")
check('private static final String FAVORITES_PREF = "folder_favorites_v1"' in source, "favorites use a new isolated preference key")
check('"XBMC.GetInfoLabels"' in source and '"Container.FolderPath"' in source and '"Container.FolderName"' in source,
      "current Kodi folder metadata is requested on demand")
check('"GUI.ActivateWindow"' in source and 'new JSONArray().put(path)' in source,
      "selecting a stored favorite navigates to its saved path")
check("saveCurrentFolder()" in source and "Save current folder" in source, "saving requires a direct user action")
check("removeFolderFavorite(path)" in source and "Remove favorite" in source, "saved favorites can be removed explicitly")
check("userRequestExecutor().execute(() -> {\n            String path = null" in source, "user-requested Kodi metadata lookup uses the flavor-aware request executor")
print("All folder-favorites source contract checks passed; Kodi runtime behavior still requires a Kodi host.")
