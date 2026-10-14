# Xperia E2003 OS readiness snapshot

Date: 2026-10-14  
Firmware: Sony 25.0.A.2.31, Android 4.4.4 / API 19  
Device: Xperia E2003  
Purpose: read-only continuation check for the FarfarRemote OS track

## Actions and safety

- Rebooted from Android to Fastboot and back to Android. No unlock, flash, erase, or partition write command was issued.
- Fastboot reported product `E2003`, bootloader `S1_Boot_MT6732_TC9PRA_9`, baseband/firmware `25.0.A.2.31`, and `secure: yes`.
- `fastboot getvar unlocked` returned an empty value. `fastboot oem device-info` returned `unknown command`; this bootloader did not provide an independent unlock-state confirmation through those read-only queries.
- The owner reports that the bootloader is unlocked. The Android ADB shell still runs as UID 2000 (`shell`), and no `su` was found in the checked standard paths. Root access is therefore not available in the current Android session.
- No package, app data, Wi-Fi configuration, or system file was changed.

## Startup and runtime observations

- FarfarRemote OS package `org.farfarremote`, version `0.4.2-rc1`, remained installed.
- After reboot, Activity Manager showed `org.farfarremote/.MainActivity` as the HOME task. This confirms launcher resolution after reboot, but is not a timed cold-boot measurement.
- At approximately 136 seconds uptime, `dumpsys meminfo org.farfarremote` reported total PSS of **7,352 kB** (about **7.2 MiB**) and private dirty memory of **5,504 kB**. This is a single post-reboot sample, not a before/after comparison.
- `/proc/meminfo` at an earlier post-reboot sample reported `MemTotal` 918,424 kB, `MemFree` 273,640 kB, `Cached` 348,592 kB, `Active` 102,068 kB, and `Inactive` 315,104 kB. Linux page cache is reported separately from process PSS; these values should not be summed as if they were independent RAM pools.
- A short `dumpsys cpuinfo` interval around 136 seconds uptime reported FarfarRemote at approximately **0.5% CPU** and total CPU rounded to **0%** for that interval. Background compilation and other activity were still visible, so this is not a settled idle baseline.
- Wi-Fi remained enabled but showed `SCANNING` / `DISCONNECTED` after the reboot and over a further 25-second check. Do not treat Kodi connectivity as verified in this session. Check that the configured access point is in range and reconnect through Android Settings if required; no network configuration was altered.

## Conclusions

- The existing OS app and HOME selection survived the reboot.
- The reported unlocked bootloader has not been independently confirmed by the available Fastboot query responses. This does not change the observed fact that Android ADB is unprivileged and not rooted.
- There is still no verified root/recovery image or safe, reproducible root procedure for this exact E2003 firmware. Historical 2016 KingRoot claims are anecdotal and are not a recommended procedure.
- Phase A reversible package disabling remains unavailable through the previously tested ADB and Appinfo routes. Do not substitute uninstall or system partition edits.
- Wi-Fi reconnection needs a manual check before claiming a complete post-reboot Kodi regression pass.

## Next safe steps

1. Confirm Wi-Fi reconnects and Kodi control works after this reboot.
2. Capture a separate cold-boot-to-launcher timing using a stopwatch or timestamped video over multiple boots; do not infer it from the uptime snapshot.
3. If OS debloating remains a priority, first establish a verifiable recovery path and a trusted, exact-device privilege method. No such method is currently approved or ready to run.
