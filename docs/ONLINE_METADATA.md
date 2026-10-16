# Automatic Online Media Descriptions

The App and OS editions share the same opt-in lookup. The `Auto-scrape English descriptions` setting is off by default. When enabled, FarfarRemote only searches for the currently playing movie or series when Kodi has not provided a plot. It does not scan folders or modify Kodi's library.

## Provider order

1. Kodi's own library metadata remains the preferred result.
2. For TV episodes, or media Kodi tags as anime, FarfarRemote queries AniList using the series/title name. It accepts a conservative title match and only displays descriptions that pass a basic English-text check.
3. If AniList has no suitable English result, FarfarRemote searches English Wikipedia through the MediaWiki Action API. Wikipedia is also tried first for other films and TV content.
4. If Wikipedia has no suitable page, FarfarRemote checks Wikidata for a short English catalog description. AniList is the final fallback for possible anime feature films.
5. If none returns a matching description, the information page says so and keeps the remote usable.

No account, user-entered API key, Kodi video-source setup, or Kodi scraper configuration is required. Queries are sent only while the opt-in is enabled. Results are stored in the app's private preferences, capped at 40 titles, and the source line links to the originating page. App and OS share the user's existing preference key so an update does not reset the setting.

## Source and licensing notes

- [AniList API](https://anilist.gitbook.io/anilist-apiv2-docs/): used for anime titles and short descriptions. The result links to the corresponding AniList entry.
- [English Wikipedia / MediaWiki API](https://www.mediawiki.org/wiki/API:Search): used as the broad fallback for film and TV titles. Text is labeled with its source, article link, and [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) notice.
- [Wikidata API](https://www.wikidata.org/w/api.php): used only as a concise English catalog-description fallback, not represented as a full plot synopsis. Wikidata structured data is [CC0](https://creativecommons.org/publicdomain/zero/1.0/), and each result links to its item page.
- IMDb is not automatically queried. IMDb's published guidance prohibits automated extraction from its website and limits its downloadable datasets to personal, non-commercial use; those datasets also do not provide the story summaries needed here. The app keeps its existing user-initiated IMDb link.
- TMDB is not included. Its API requires a key issued to the project and attribution. A private credential should not be shipped in a public APK; adding it would require a project-maintained proxy or another safe credential arrangement. Users are not asked to supply a key.

## Request and failure behavior

Requests use HTTPS, run on a dedicated background executor, have connection/read timeouts, and cap response bodies at 1 MiB. Provider/network/parse failures are treated as no result and do not block Kodi controls. The legacy Android 4.4 device may fail to connect if its system TLS trust store cannot validate a provider's current certificate; in that case Kodi metadata and manual IMDb lookup remain available.

The English-language check is intentionally lightweight rather than a language-identification service. AniList descriptions without common English markers or containing non-Latin writing are skipped; Wikipedia requests are explicitly sent to English Wikipedia. Search can still miss alternate titles, ambiguous titles, or locally named files.
