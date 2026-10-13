# Settings graphics: source and license note

## Canonical source

The v0.3 Settings package supplied for this project is kept unpacked at `FarfarRemote_Settings_Assets_v0.3/`. It contains 40 files: 38 PNG images, a README, and a design instruction. The root ZIP contains the same 40 paths and byte-identical contents, so Git ignores the ZIP and tracks the extracted directory as the single canonical source. Original PNGs in that directory are not modified.

All 38 PNGs are RGBA. The two screen backdrops are opaque, at 540×960 portrait and 960×540 landscape. Transparent components have alpha samples from 0 to 255. Buttons, icons, inputs and switches are separate images; there is no combined button sheet. The 1536×1024 visual reference has a partial alpha channel and is a mockup only.

## Android derivatives

The Settings UI uses the supplied portrait/landscape backgrounds, header and section strips, input backgrounds, orientation choices, primary/secondary/coffee button backgrounds, toggle track/thumbs, and settings/wifi/display/remote/info/orientation/test/save/coffee/arrow icons. Source 128×128 icons are downscaled to 64×64 RGBA PNGs; other selected graphics retain their source dimensions. Android references these assets at `drawable-nodpi` to avoid density-dependent resampling. Views render all changing text, credentials and state dynamically.

The empty Settings cards are Android `GradientDrawable` shapes. The input and orientation states use XML selectors. No logo or official Buy Me a Coffee brand artwork is used; the coffee cup and button are the generic user-supplied assets. The large reference mockup and unused assets are not packaged into the APK.

## License

The repository's application source is GPL-3.0, as stated by the repository license. The supplied Settings pack does not declare a separate copyright holder or asset-specific license in its README or instruction file. The files are retained and used as assets provided for this project; that does not establish a license for unrelated reuse. Confirm the asset contributor's distribution rights before reusing this graphics pack outside FarfarRemote OS. No third-party logo license is implicated by the generic coffee icon.
