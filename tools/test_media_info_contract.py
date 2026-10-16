#!/usr/bin/env python3
"""Source-contract checks for the experimental Kodi media-information view.

These checks verify wiring and preservation guards only; they do not replace a Kodi/device test.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "app/src/main/java/org/farfarremote/MainActivity.java").read_text()
online = (ROOT / "app/src/main/java/org/farfarremote/OnlineMetadataClient.java").read_text()
kodi = (ROOT / "app/src/main/java/org/farfarremote/KodiClient.java").read_text()

def check(condition, message):
    if not condition:
        print(f"FAIL: {message}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {message}")

check('client().snapshot(inMediaInfo || prefs.getBoolean(AUTO_ONLINE_METADATA_PREF, false))' in main,
      "extended Kodi metadata is requested in the details view or by explicit online-lookup opt-in")
check('Snapshot snapshot() throws KodiException { return snapshot(false); }' in kodi,
      "existing snapshot callers retain the original no-extra-metadata behavior")
check('if (includeExtendedMediaDetails)' in kodi and 'catch (KodiException e) { android.util.Log.d("FarfarRemote", "Extended media details unavailable:' in kodi,
      "extended fields are optional and cannot fail the established snapshot")
check('put("title").put("showtitle").put("episode").put("season").put("thumbnail").put("artist").put("album").put("file")' in kodi,
      "existing Now Playing item fields remain requested")
for field in ("plot", "plotOutline", "genres", "year", "director", "studio", "rating", "contentRating", "imdbId", "tagline"):
    check(f"p.{field} =" in kodi, f"Kodi metadata parser maps {field}")
check('pointInside(nowPlayingGestureView' in main and 'showMediaInfo(false)' in main,
      "a horizontal swipe over the Now Playing header opens the information page")
check('LinearLayout card = new LinearLayout(this); card.setOrientation(LinearLayout.HORIZONTAL);' in main
      and 'root.addView(card, cardLp);' in main,
      "media summary card is attached to its parent exactly once")
check('showMediaInfo(true)' in main and 'Now Playing information' in main,
      "Kodi Library exposes an explicit information-page control")
check('IMDb' in main and 'https://www.imdb.com/title/' in main and 'https://www.imdb.com/find/?q=' in main,
      "IMDb ID and title-search fallbacks are available")
check('https://anilist.co/search/anime?search=' in main and 'contains("anime")' in main,
      "Kodi-tagged anime exposes an AniList title search")
check('Kodi is connected, but no media is active.' in main and 'No English description was found.' in main,
      "missing metadata and idle playback have explicit UI fallbacks")
check('No active Kodi connection.' in main and 'infoImdbButton.setVisibility(p != null ? View.VISIBLE : View.GONE)' in main,
      "offline idle view is truthful and hides unusable external lookups")
check('prefs.getBoolean(AUTO_ONLINE_METADATA_PREF, false)' in main and 'Auto-scrape English descriptions' in main,
      "online metadata lookup is a shared, off-by-default Settings option")
check('https://graphql.anilist.co' in online and 'type: ANIME' in online,
      "anime lookup uses the AniList API")
check('https://en.wikipedia.org/w/api.php' in online and 'English Wikipedia (CC BY-SA 4.0)' in online,
      "general fallback uses English Wikipedia and identifies its license/source")
check('https://www.wikidata.org/w/api.php' in online and 'Wikidata (CC0)' in online,
      "short English catalog-description fallback uses Wikidata")
check('metadataRequests.execute' in main and 'metadataLookupAttempted.add(key)' in main,
      "provider lookups run off the UI thread and are deduplicated per title")
check('IMDb remains available as a manual' in (ROOT / "README.md").read_text() and 'IMDb is not automatically queried' in (ROOT / "docs/ONLINE_METADATA.md").read_text(),
      "IMDb website scraping is not used")
print("All media-information source-contract checks passed; runtime Kodi behavior remains to be tested.")
