# Battery and performance plan

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

## Current evidence

- **REPORTED:** owner estimates roughly 12 hours in earlier real use. This is not a controlled measurement.
- **VERIFIED:** Sony's 2015 white paper lists a 2,300-mAh minimum embedded battery and laboratory standby/music/video figures. These historic lab figures are not a prediction for a worn battery or always-on Kodi remote.
- **VERIFIED:** current battery tooling exists in `tools/battery_measure.py` and `tools/compare_battery_sessions.py`; it records real elapsed time, battery stats and rejects USB/AC-powered sessions.
- **VERIFIED:** the phone was USB-powered during this research. Current `dumpsys battery` was a powered snapshot, not an endurance sample. No baseline or optimized battery session was collected.
- **UNKNOWN:** present battery health/capacity, actual average current, deep-sleep residency, Wi-Fi suspend behavior over long periods and screen-off runtime.
- **BLOCKED:** a meaningful baseline/comparison cannot be recorded while the phone is USB-powered; an unplugged session is still required.

Prior OS Battery Mode implementation details and limitations are in [`docs/OS_BATTERY_OPTIMIZATION.md`](../../docs/OS_BATTERY_OPTIMIZATION.md).

## Likely energy contributors to measure

1. Display brightness and time on: likely dominant during active use; use Android timeout, modest brightness and retain instant wake.
2. Wi-Fi association/retries and periodic JSON-RPC: measure connected idle and disconnected scenarios separately; exponential backoff already exists in OS Battery Mode.
3. CPU awake time from polling, NSD and UI callbacks: confirm screen-off poll suspension, no wake locks, and deep sleep using batterystats/kernel counters where available.
4. Cellular scanning/background sync/GPS: owner intends dedicated operation; compare reversible manual settings only after verifying Wi-Fi reconnects after reboot.
5. Battery aging/temperature: repeat matched tests at similar temperature; do not infer mAh/current from voltage or a short percentage delta.

## Controlled test plan

Use the existing battery measurement scripts, same unplugged E2003, same battery/Wi-Fi AP/brightness/Kodi condition/room temperature and matched duration. Test: screen-off idle, screen-on idle, Kodi connected idle, playback, Kodi disconnected, and realistic intermittent use. Allow a five-minute settling interval. Capture at least several hours per case; percentage quantization makes short runs weak evidence. Save output outside Git because it is device-specific.

Report observed elapsed time and start/end percentage/voltage/temperature/status, charging flag, screen state, FarfarRemote process, CPU deltas and batterystats. Do not produce a 24-hour estimate from a short test. A 24-hour target is **UNKNOWN/not evidenced**.

## Reversible manual candidates

- Android Wi-Fi advanced setting “Keep Wi-Fi on during sleep”, if present: verify Kodi reconnect and FarfarRemote wake control after screen-off and reboot. Sony firmware may override standard Android behavior.
- Airplane mode then manually re-enable Wi-Fi may reduce cellular radio activity but can interfere with boot reconnection, NSD or Sony services; test as a reversible user setting only.
- Turn off location and account/background sync if not used; verify none are required by Wi-Fi setup or device management.
- Test Sony STAMINA only if it is available on this firmware and configure FarfarRemote/network access exemptions if supported. It can suppress network/background activity; never assume it is safe for Kodi connectivity.
- Do not change CPU governor, frequency, kernel config or protected packages without root, baseline data and a recovery plan.

## Acceptance criteria

No user command may be delayed for battery savings. After screen wake, first Kodi command and status must respond promptly; Wi-Fi must return after sleep and reboot. Compare paired sessions against Normal mode before enabling any battery profile by default. A claimed improvement must exceed run-to-run variance and be repeatable.
