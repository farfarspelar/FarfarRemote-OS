# Experimental test plan

## Offline gates (before any device write)

1. Confirm source image, APK signer/package/min API and animation hashes.
2. Build a new output image only; retain its SHA-256 and full build log.
3. Run `e2fsck -fn`, verify APK/animation by debugfs readback, and inspect owner/mode/SELinux metadata.
4. Independently inspect filesystem size, free blocks, `/build.prop`, launcher intent and boot-animation path.
5. Create a specific operation proposal with exact partition mapping, image hash, current backup state, failure modes and recovery method. Stop for separate explicit authorization before any write.

## First boot checks (only after an authorized write plan)

Observe boot completion and ADB availability. Check boot logs and verify: touch/display, HOME selection, Settings and input, Wi-Fi association/reconnection, Kodi discovery/manual connection, navigation, Audio/Subtitles, screen timeout, USB/ADB, charging state, temperature and idle suspend/resume. Test reboot and power interruption only after basic boot is stable.

## Stop criteria

Stop further changes if boot loops, ADB is unavailable beyond the agreed observation window, display/touch fails, Wi-Fi cannot recover, charging/battery reporting is abnormal, or the image writes outside the exact approved partition. Do not try unrelated partitions or generic images as recovery attempts.

No hardware test has been performed with the v0.1 system image. Existing user verification on stock Android does not count as a v0.1 ROM test.
