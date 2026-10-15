# Experimental test plan

## Offline gates (before any device write)

1. Confirm source image, APK signer/package/min API and animation hashes.
2. Build a new output image only; retain its SHA-256 and full build log.
3. Run `e2fsck -fn`, verify APK/animation by debugfs readback, and inspect owner/mode/SELinux metadata.
4. Independently inspect filesystem size, free blocks, `/build.prop`, launcher intent and boot-animation path.
5. Create a specific operation proposal with exact partition mapping, image hash, current backup state, failure modes and recovery method. Stop for separate explicit authorization before any write.

## First boot checks (only after an authorized write plan)

Observe boot completion and ADB availability. The live R7A user data currently records FarfarRemote (`org.farfarremote/.MainActivity`) as preferred HOME; preserve `/data` for the first system-image trial and confirm this preference survives Package Manager's system-app scan. If it does not, use the Sony launcher/Settings or ADB to select FarfarRemote. Check boot logs and verify: touch/display, HOME selection, Settings and input, Wi-Fi association/reconnection, Kodi discovery/manual connection, navigation, Audio/Subtitles, screen timeout, USB/ADB, charging state, temperature and idle suspend/resume. Test reboot and power interruption only after basic boot is stable.

### Attempt log — 2026-10-15

An owner-authorized `fastboot boot` attempt used the local boot-container POC (SHA-256 `1d71c03b172d23b7830922153559df37966321bd28fbb9a28666fd81268543dc`). Fastboot acknowledged transfer, then reported a USB status-read failure as the phone re-enumerated with a mass-storage-only USB function. No ADB/Fastboot return was observed during the test window, so boot result is **INCONCLUSIVE**. No flash/erase/unlock/wipe command was used. This did not test the custom `/system` image; the installed system partition remained untouched.

## Stop criteria

Stop further changes if boot loops, ADB is unavailable beyond the agreed observation window, display/touch fails, Wi-Fi cannot recover, charging/battery reporting is abnormal, or the image writes outside the exact approved partition. Do not try unrelated partitions or generic images as recovery attempts.

No hardware test has been performed with the v0.1 system image. Existing user verification on stock Android does not count as a v0.1 ROM test.
