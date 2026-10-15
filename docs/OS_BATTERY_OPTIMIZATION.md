# FarfarRemote OS Battery Optimization — Phase 1

## Status

This document separates source inspection and live, read-only observations from measured battery endurance. No battery improvement or 24-hour runtime is claimed yet.

## Baseline implementation inspected

- The Activity starts one Kodi snapshot immediately from `onStart()` and schedules another after each snapshot. The normal interval is 2.8 seconds.
- `KodiClient.snapshot()` may issue several sequential JSON-RPC HTTP requests: connectivity/name, volume, active-player lookup, progress, audio streams, subtitles, and item metadata. A media-playing cycle can therefore create several requests, rather than one request every 2.8 seconds.
- The existing poll loop checks every 3 seconds while Settings is open even though it does not query Kodi in that state.
- `onStop()` removes the pending poll and discovery listener; `onStart()` resumes polling. There is no application-held wake lock. Phase 1 will also explicitly stop OS-track polling on screen-off and resume immediately on screen-on, since lifecycle callbacks alone are not a strong screen-state contract.
- A failed Kodi snapshot currently retries at the normal 2.8-second interval. This can repeat HTTP connection/read timeouts and is the clearest avoidable background network/CPU cost when Kodi or Wi-Fi is unavailable.
- User commands and Kodi polling currently share one single-thread executor. A command can sit behind a multi-request snapshot. Phase 1 will separate user-triggered Kodi commands from background snapshots so polling policy cannot queue user input.
- The existing `keep_awake` preference defaults to `false`; otherwise the Activity toggles `FLAG_KEEP_SCREEN_ON`. When off, Android's configured timeout applies. The connected Xperia currently reports a 30,000 ms timeout.
- Brightness is currently left to Android's system setting. No battery brightness override exists.
- Find My Kodi uses on-demand NSD discovery with an 8-second timeout and is stopped on Activity stop. It does not scan continuously.
- Artwork is requested only when the thumbnail path changes. It has connect/read timeouts and is decoded off the UI thread.
- The App and OS flavors share Java code, but OS-specific resources identify the dedicated OS flavor. Battery profiles will be gated by that resource so App behavior stays unchanged.

## Live device observation before code changes

ADB identified the attached device as the E2003 family with Android 4.4.4/API 19. It currently runs FarfarRemote OS 0.4.3-rc1. The display was off, Android reported a 30-second screen timeout, no active Power Manager wake lock, and USB charging was enabled. Battery level was 100% while USB-powered. These are a point-in-time diagnostic snapshot only; they are not a battery-endurance baseline.

The available `dumpsys batterystats` history contains mixed earlier screen, Wi-Fi, GPS, and wake-lock events from unrelated prior activity. It cannot isolate FarfarRemote's drain. Continuous ADB over USB also powers the phone and invalidates endurance measurements. No clean, unplugged, comparable baseline session is currently available.

After the in-place 0.4.5-rc1 OS APK update, a later read-only connectivity snapshot reported Wi-Fi connected while the display was asleep. This is a single observation; it does not establish continuous Wi-Fi retention through a long sleep or successful Kodi reconnection.

## Phase 1 implementation

The OS flavor now has opt-in Battery Mode controls:

- **Normal** retains the current foreground polling cadence for familiar behavior.
- **Balanced** keeps 2.8-second refresh after recent input, polls active playback every 5 seconds, and uses the selected 2/5/10-second interval when Kodi is connected but idle.
- **Maximum Battery Saving** keeps 2.8-second refresh after recent input, polls active playback every 10 seconds, and uses the selected 2/5/10-second interval when Kodi is connected but idle.
- Disconnected retries use bounded exponential backoff (2, 4, 8, 16, then 30 seconds) while Auto Reconnect is enabled. When it is disabled, background reconnect polling stops; a user command or Test Connection remains available.
- A lifecycle-scoped screen receiver removes scheduled Kodi polling on screen-off. Screen-on schedules an immediate refresh. No wake lock is acquired.
- Polling stops while OS Settings are open and resumes immediately when Settings closes. Find My Kodi remains on-demand and retains its existing timeout/lifecycle cleanup.
- An OS-only Reduced Brightness option applies a 25% window brightness while FarfarRemote is visible. It is off by default and does not change Android's saved brightness. Android's normal display timeout remains the default; the existing Keep Screen Awake switch remains available.
- OS Kodi input commands, track reads/selections, connection checks, and folder reads use a separate serialized executor from background snapshots so a status poll cannot queue a user request. The App flavor continues using its original executor.

Preferences use new `os_battery_*` keys. Existing Kodi, orientation, keep-awake, and reconnect preference keys are not changed. App flavor code paths retain their existing poll cadence and UI.

The initial profile is **Normal** to avoid changing existing OS behavior on upgrade. Battery settings do not write Android system settings. Custom screen timeouts are not stored by the app; adjust the system timeout in Android Display Settings if needed.

## Measurement procedure

Use `python3 tools/battery_measure.py --label baseline --scenario screen_off_idle --duration-seconds 3600 --interval-seconds 60` to capture a read-only E2003 battery session through wireless ADB. Supported scenarios are `screen_off_idle`, `screen_on_idle`, `kodi_connected_idle`, `kodi_playback`, `kodi_disconnected`, and `intermittent_use`. It records actual host elapsed time, battery percentage/voltage/temperature/status, whether AC/USB was connected, screen state, CPU counters, FarfarRemote process information, Wi-Fi state, and start/end `dumpsys batterystats` output. It refuses USB ADB and any detected AC/USB charging. Use `python3 tools/compare_battery_sessions.py BASELINE_DIR OPTIMIZED_DIR` to compare matching scenarios without projecting runtime.

For a meaningful comparison:

1. Use the same device, battery, Wi-Fi access point, Kodi state, screen mode, brightness, temperature, and radio configuration.
2. Let the phone settle for five minutes before each session.
3. Keep it unplugged. Prefer a test setup that does not need a USB cable; if ADB-over-Wi-Fi is used, note that its traffic is part of the scenario.
4. Record the exact scenario: screen-off idle, screen-on idle, Kodi connected/idle, active playback, Kodi disconnected, or intermittent real use.
5. Capture baseline and optimized runs for the same elapsed duration. Short sessions with only 1% battery change are too coarse for a reliable rate.
6. Do not infer battery capacity or current draw from voltage, level, or `dumpsys batterystats` unless the firmware provides a validated measurement.

### Results

- Baseline endurance estimate from the project owner: approximately 12 hours, unverified.
- Baseline battery session recorded by Phase 1 tooling: none. The measurement tool was run against the attached E2003 and correctly refused because USB charging was active.
- Optimized battery session: none yet.
- **Informal unplugged observation (2026-10-15):** the owner reported 97% at 20:19 and 96% at 21:31, with the phone unplugged for the entire 72-minute interval. This is a one-percentage-point change from rounded Android battery readings during an uncontrolled first-boot validation period. Screen state, Wi-Fi/playback activity, temperature and exact usage were not held constant or logged, so this is not a comparable scenario measurement and does not support a drain-rate or endurance projection.
- **Abrupt level change after power cycle (2026-10-15):** after that observation, the owner powered the phone off for about one minute. On restart the indicator showed 6%, and the owner connected a wall charger. No battery voltage or current sample was captured for the event. This is recorded as a sudden reported state-of-charge change, not as 90 percentage points consumed while powered off. Gauge recalculation, cell voltage sag, battery aging, or another battery/firmware issue cannot be distinguished from the available data. E4g owner reports describe similar abrupt percentage drops, but those forum reports are anecdotal and do not diagnose this device: [Sony Community E4g battery thread](https://community.sony.es/t5/e-series/battery-backup-issue-xperia-e4g/m-p/3410074/highlight/true).
- **Follow-up charging-screen reading (2026-10-15):** after the owner powered the phone off and connected the wall charger, the charging screen displayed 96% again. The elapsed time was not recorded and no voltage/current sample was taken. The 6% and 96% readings are therefore inconsistent reports from successive power states; neither establishes the true state of charge. Battery percentage should not be used for endurance conclusions until the behavior is understood.
- The owner subsequently started the phone after charging to a displayed 6%. FarfarRemote launched automatically and reconnected to Kodi without interaction. This confirms the OS startup path worked at that displayed reading; it does not validate the battery's actual remaining capacity.
- 24-hour target: not assessable from current evidence. The present USB-powered point-in-time snapshot does not support an endurance estimate.

Both App and OS flavors compile after the Phase 1 changes. Automated source-contract checks cover OS-only gating, profile intervals, backoff limits, screen receiver lifecycle, OS-only command/poll executor separation, retained preferences, and charging rejection. They are not runtime tests. The 0.4.5-rc1 OS APK was installed in place, but the Android Keyguard prevented UI and screen-receiver runtime verification. No Kodi host was used for an input round-trip.

## Compatibility and protected behavior

- Minimum API remains 19; OS target remains 28; compile SDK remains 36.
- Screen-state broadcasts, `PowerManager.isScreenOn()`, `SystemClock.elapsedRealtime()`, window brightness attributes, handlers, and radio controls are available on the E2003's API 19. No root, settings-provider write, package disable, firmware change, or new permission is required.
- Battery controls are rendered only by the OS flavor. The regular App keeps its existing controls and polling behavior.
- Screen timeout is not written by FarfarRemote. Users may adjust it in Android Display Settings; those system choices remain in effect.
- Wi-Fi and saved-network settings are not modified. Android/Sony may suspend Wi-Fi based on its own sleep policy; reconnect after screen wake must be checked on the physical phone.

## Known limits and next work

- The present ADB session is USB-powered, so no valid runtime comparison can be captured now.
- Android 4.4 battery statistics are coarse and may include system-wide/previous history. Battery percentage is quantized and an aged battery can vary with temperature and wear.
- Screen-off suspension depends on the device delivering Android's screen-state broadcast; this needs physical validation across sleep/wake and reboot.
- The Battery Mode default is Normal to preserve the current OS behavior. A/B measurement is needed before considering a different default.
- Reduced brightness may make the remote harder to use; validate its chosen level in the actual room.
- The OS's Wi-Fi sleep policy and Sony STAMINA/SuperStamina behavior are firmware-dependent. No system setting is changed automatically. For a dedicated controller, first test Android Settings > Wi-Fi > Advanced > Keep Wi-Fi on during sleep (if present) with the screen-off/reconnect scenario. Airplane mode with Wi-Fi re-enabled can reduce cellular scanning but may alter boot/reconnect behavior; only try manually and verify Wi-Fi after reboot. Keep mobile radios/location/background sync disabled manually only if they are not used; do not disable Sony power-management components or packages via ADB.
