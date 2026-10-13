# Graphic assets and Android derivatives

FarfarRemote UI artwork and visual reference images were generated with ChatGPT from prompts written by the project owner, who directed the visual design. The generated images were integrated into the project as controls, logos, backgrounds, and references. See [ASSET_PROVENANCE.md](../ASSET_PROVENANCE.md) for the public provenance and third-party mark review.

## Remote controls

`originals/` retains byte-for-byte copies of the supplied source PNGs. The app uses trimmed, proportion-preserving, lossless RGBA derivatives under `app/src/main/res/drawable-nodpi/`; nodpi avoids density-based resampling on the 240 dpi E2003.

| File | Source dimensions / mode | Alpha and use |
|---|---|---|
| `button_dpad_ok.png` | 1254×1254 RGBA | One transparent D-pad; UI maps separate non-overlapping direction and OK touch zones. |
| `button_volume_rocker.png` | 1024×1536 RGBA | Transparent rocker; top, bottom, and mute zones are handled separately. |
| `buttons_core_actions_sheet.png` | 2172×724 RGBA | Five controls cropped individually: Back, Home, Play/Pause, Stop, Settings. |
| `buttons_transport_sheet.png` | 2172×724 RGBA | Four controls cropped individually: Rewind, Previous, Next, Fast Forward. |
| `buttons_media_categories_sheet.png` | 2172×724 RGBA | Four controls cropped individually: Movies, TV Shows, Music, Add-ons. |
| `button_audio_selector.png` | 2172×724 RGBA | Generic Audio selector; current track is dynamic Kodi text. |
| `button_subs_selector.png` | 2172×724 RGBA | Generic Subtitles selector; current track and Off state are dynamic. |
| `button_side_nav.png` | 1024×1536 RGBA | Transparent side control retained as source; not used by the current action map. |
| `button_menu.png` | 1254×1254 RGBA | Transparent menu artwork retained as source; not required in the action map. |
| `button_connection_status.png` | 2172×724 RGBA | Contains baked-in sample host/status and is excluded from live status UI. |
| `farfarremote_os_boot_logo.png` | 1254×1254 RGBA | Transparent FarfarRemote project logo used for the brief app startup overlay. |
| Portrait / landscape references | 941×1672 and 1672×941 RGB | Opaque design mockups only; never used as full-screen app backgrounds. |

UI images use alpha channels. Button sheets are cropped into individual assets at equal cell boundaries and then trimmed to visible bounds. Android views provide touch regions, captions, accessibility labels, and changing status text. Kodi artwork is downsampled before display; the missing-art placeholder is a small local graphic.

## Settings graphics

The unpacked `FarfarRemote_Settings_Assets_v0.3/` directory is the canonical original source; the ZIP duplicate is excluded from Git. Its PNGs and generated references were inspected for dimensions, alpha, and use. Separate button and icon files remain individual images; there is no combined button sheet. The reference mockup is not packaged into the APK. Selected small icons are reduced to 64 px for app resources.

The Settings panel backgrounds and buttons are generated project artwork. Dynamic labels, password fields, selection states, and status indicators are Android views/XML selectors rather than baked text. The coffee-cup icon is generic project artwork; no official Buy Me a Coffee branding is used.

## Screenshots

The public README screenshots under `docs/screenshots/` are direct captures of the App variant on the project's Xperia E4g E2003. They show an offline preview and contain no configured Kodi host or credentials. They are documentation captures, not packaged app artwork.

## License and trademarks

Project source code is GPL-3.0. The graphics are documented as ChatGPT-generated project assets from owner-written prompts. No third-party stock graphics or official Kodi/Buy Me a Coffee logos have been identified in the app resources. Product names “Kodi” and “Buy Me a Coffee” are used only to describe interoperability and an external link; their respective marks remain owned by their owners. See [ASSET_PROVENANCE.md](../ASSET_PROVENANCE.md).
