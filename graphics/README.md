# Graphic asset review and Android derivatives

`originals/` is a byte-for-byte copy of every PNG supplied under `FarfarRemote_Asset_Pack/assets/`. The original pack and its mockups are also left in place. App resources are trimmed to their alpha bounds (with a small edge pad), resized with Lanczos and saved losslessly as RGBA PNGs under `app/src/main/res/drawable-nodpi/`; nodpi prevents density-based resampling on the 240 dpi E2003. This directory is not packaged in the APK.

## Source image checks

| File | Source dimensions / mode | Alpha and handling |
|---|---|---|
| `button_dpad_ok.png` | 1254×1254 RGBA | Transparent outside the control; one D-pad, mapped to five non-overlapping polar touch zones (center OK plus four directional sectors). |
| `button_volume_rocker.png` | 1024×1536 RGBA | Transparent outside rocker; separate top/bottom hit zones and central mute zone. |
| `buttons_core_actions_sheet.png` | 2172×724 RGBA | Five equal-width controls split into Back, Home, Play/Pause, Stop, Settings. |
| `buttons_transport_sheet.png` | 2172×724 RGBA | Four equal-width controls split into Rewind, Previous, Next, Fast Forward. |
| `buttons_media_categories_sheet.png` | 2172×724 RGBA | Four equal-width controls split into Movies, TV Shows, Music and Add-ons. |
| `button_audio_selector.png` | 2172×724 RGBA | Transparent Audio selector; its fixed label is generic. Current track is a separate Kodi-driven TextView. |
| `button_subs_selector.png` | 2172×724 RGBA | Transparent Subtitles selector; its fixed label is generic. Current track/Off is dynamic text. |
| `button_side_nav.png` | 1024×1536 RGBA | Transparent side rocker retained as an original; not used in this layout because D-pad and separate actions already cover navigation. |
| `button_menu.png` | 1254×1254 RGBA | Transparent menu/control artwork retained as an original; not needed by the current action map. |
| `button_connection_status.png` | 2172×724 RGBA | Transparent, but includes baked-in “Kodi · MeLE / Connected”; deliberately not used for live status. Host and connection state are dynamic text. |
| `farfarremote_os_boot_logo.png` | 1254×1254 RGBA | Transparent logo; used on the app startup overlay only. |
| Portrait / landscape references | 941×1672 and 1672×941 RGB | Opaque mockups containing a phone and sample content; design references only, never screen backgrounds. |

Every source UI control is RGBA. Sampled corners/edges were checked for alpha zero; some artwork reaches a canvas edge, so the alpha bounding boxes vary. The UI icons are used as button faces; captions/accessibility descriptions and touch containers remain Android views. Kodi artwork is downsampled to about 256 px per side and decoded to RGB_565. Missing art uses a small neutral local placeholder.

The three sheets have equally spaced four/five-cell layouts. Their crop edges are the equal cell boundaries; alpha trimming removes each neighbor's transparent gap. The source files remain untouched. The hard-coded status asset and the full-screen mockups are excluded from Android resources.
