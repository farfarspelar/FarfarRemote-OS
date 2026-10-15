# Hardware compatibility matrix

| Component | Evidence in v0.1 | Status |
|---|---|---|
| Target identity | Live handset reports E2003, Android 4.4.4, `25.0.A.2.31`, CDA `1293-7358 R7A` | **VERIFIED on stock only** |
| `/system` content | Reconstructed R7A metadata/payloads over E2003 R10A ext4; prior 4,447 metadata entries and 4,193 file hashes matched | **Previously validated reconstruction** |
| `/system` image geometry | The built ext4 image is 2,097,152,000 bytes; live `/proc/partitions` reports `system` as 2,048,000 × 1,024-byte blocks, also 2,097,152,000 bytes | **Exact size match; packaging/write/boot compatibility not established** |
| Kernel/boot chain | R10A/R3A E2003 25.0.A.2.31 Sony ELF boot payloads cross-match; a legacy Android boot-container POC was sent with `fastboot boot`, but the host lost USB during handoff and no boot-completion signal was observed | **INCONCLUSIVE hardware RAM-boot attempt; no partition write; exact live-R7A boot artifact remains unknown** |
| Display/touch | Stock R7A files retained | **Not tested with experimental image** |
| Wi-Fi/reconnect | Stock R7A files retained; owner reports stock Wi-Fi survives reboot | **Not tested with experimental image** |
| Audio | Stock R7A files retained | **Not tested with experimental image** |
| USB/ADB | Stock R7A files retained; host saw E2003 over ADB and Sony S1 service mode | **Not tested with experimental image** |
| Charging/battery | Stock R7A power stack retained | **Not tested with experimental image** |
| Android HOME / Kodi | Existing signed FarfarRemote OS APK inserted | **Static package/signature check only** |
| Boot animation | ZIP format, CRC, frame geometry checked; installed in offline `/system` image | **Not playback-tested** |

An ext4 filesystem can be perfectly valid and still be rejected, mounted differently, or fail after boot due to image packaging, partition geometry, verity/signature policy, SELinux/runtime integration, or mismatched boot components.
