# Hardware compatibility matrix

| Component | Evidence in v0.1 | Status |
|---|---|---|
| Target identity | Live handset reports E2003, Android 4.4.4, `25.0.A.2.31`, CDA `1293-7358 R7A` | **VERIFIED** |
| `/system` content | Reconstructed R7A metadata/payloads over E2003 R10A ext4; prior 4,447 metadata entries and 4,193 file hashes matched | **Previously validated reconstruction** |
| `/system` image geometry | The built ext4 image is 2,097,152,000 bytes; live `/proc/partitions` reports `system` as 2,048,000 × 1,024-byte blocks, also 2,097,152,000 bytes; exact image was written and the phone subsequently booted | **Exact size, Fastboot write, and boot smoke test verified on E2003** |
| Kernel/boot chain | R10A/R3A E2003 25.0.A.2.31 Sony ELF boot payloads cross-match. A callass-source zImage was compiled and repacked with the R10A ramdisk using legacy geometry from an E2003 R5A recovery; the container parses and reproduces byte-for-byte. An earlier separate stock-payload container was sent with `fastboot boot`, but USB was lost during handoff and no boot-completion signal was observed. | **Static candidates only; prior RAM-boot observation is INCONCLUSIVE. No partition write; exact live-R7A boot artifact and hardware bootability remain unknown.** |
| Display/touch | Owner observed Android lock screen and selected FarfarRemote Home after experimental system boot | **Boot UI/touch interaction verified; full touch regression pending** |
| Wi-Fi/reconnect | Owner confirmed network connection on experimental image | **Wi-Fi association verified once; reboot reconnection pending** |
| Audio | Stock R7A files retained | **Not tested with experimental image** |
| USB/ADB | Host identified E2003 over ADB after experimental boot | **ADB verified** |
| Charging/battery | Host read Android battery service: 96%, USB-powered; owner reported 96% after wall charging | **Reporting verified; off-USB charging/discharging behavior pending** |
| Android HOME / Kodi | FarfarRemote launched after owner selected it as Home; owner confirmed network/Kodi control works | **HOME launch and Kodi smoke test verified; full regression pending** |
| Boot animation | ZIP format, CRC, frame geometry checked; installed in offline `/system` image; owner observed FarfarOS logo at startup | **Displayed at startup; full animation playback not separately evaluated** |

An ext4 filesystem can be perfectly valid and still be rejected, mounted differently, or fail after boot due to image packaging, partition geometry, verity/signature policy, SELinux/runtime integration, or mismatched boot components.
