# Settings asset inventory

The Settings images in `FarfarRemote_Settings_Assets_v0.3/` were generated with ChatGPT from prompts written by the project owner, who directed the visual design. The unpacked directory is the canonical source; its ZIP twin contains duplicate files and is not the app's second source.

The package contains 40 files: 38 PNG images, a README, and design instructions. All PNG files are RGBA. The two UI backdrops are opaque at 540×960 portrait and 960×540 landscape. Transparent controls, buttons, icons, fields, and switches are individual images; there is no combined button sheet. The 1536×1024 reference mockup is only a visual reference and is not packaged.

Selected backgrounds, header and section strips, inputs, orientation choices, buttons, toggle elements, and Settings icons are used by the app. Source 128×128 icons are reduced to 64×64 RGBA PNGs. Android references these images at `drawable-nodpi` to prevent density-driven resampling. All changing labels, connection data, credentials, and states are rendered by Android views.

## Branding and licensing

The coffee cup is generic generated project artwork. No official Buy Me a Coffee or Kodi logo is present in these assets. The project code is GPL-3.0; see [asset provenance](../ASSET_PROVENANCE.md) for the distinction between generated FarfarRemote assets, project code, Android platform assets, and third-party product names.
