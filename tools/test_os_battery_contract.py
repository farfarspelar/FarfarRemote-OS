#!/usr/bin/env python3
"""Source contracts for API-19-safe, OS-only battery behavior."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "app/src/main/java/org/farfarremote/MainActivity.java").read_text()
client = (ROOT / "app/src/main/java/org/farfarremote/KodiClient.java").read_text()
build = (ROOT / "app/build.gradle").read_text()
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text()
measurement = (ROOT / "tools/battery_measure.py").read_text()


def check(ok, label):
    if not ok:
        print(f"FAIL: {label}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {label}")


check("minSdk 19" in build and "targetSdk 28" in build and "versionCode 9" in build,
      "legacy API 19 OS package identity and compatibility metadata retained")
check('if (isDedicatedOs()) addBatteryModeSettings(root);' in main,
      "battery controls are added only to the OS flavor")
check('"os_battery_mode"' in main and '"os_battery_idle_seconds"' in main and '"os_battery_dim"' in main,
      "battery preferences use new, isolated keys")
check('"normal".equals(profile)) return 2800' in main and 'return "maximum".equals(profile) ? 10000 : 5000' in main,
      "Normal interval is preserved and playback intervals are profile-specific")
check('if ("2".equals(seconds)) return 2000' in main and 'if ("10".equals(seconds)) return 10000' in main,
      "idle interval choices support 2, 5, and 10 seconds")
check('return Math.min(30000L, 2000L << exponent)' in main,
      "Kodi reconnection uses bounded exponential backoff")
check('Intent.ACTION_SCREEN_OFF' in main and 'Intent.ACTION_SCREEN_ON' in main and 'handler.removeCallbacks(poll)' in main,
      "screen-off suspends scheduled polling and screen-on can resume it")
check('registerReceiver(screenStateReceiver, filter)' in main and 'unregisterReceiver(screenStateReceiver)' in main,
      "screen-state receiver is lifecycle-scoped")
check('if (isDedicatedOs() && (!screenIsOn || inSettings)) return;' in main,
      "OS status polling pauses while screen is off or Settings is open")
check('private final ExecutorService commands = Executors.newSingleThreadExecutor();' in main and
      'private ExecutorService userRequestExecutor() { return isDedicatedOs() ? commands : io; }' in main and
      'userRequestExecutor().execute(() -> { try { KodiClient client = client(); request.run(client);' in main,
      "OS user-issued Kodi actions are isolated from polling while App keeps its original executor")
check('getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)' in main and
      'WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE' in main,
      "existing Keep Screen Awake behavior and system brightness default remain")
check('android.permission.WRITE_SETTINGS' not in manifest and 'PowerManager.WakeLock' not in main,
      "no privileged settings write or wake lock was introduced")
check('"USB powered"' in measurement and '"AC powered"' in measurement and 'usb:' in measurement and 'dumpsys", "batterystats"' in measurement,
      "measurement tool rejects charging and captures Android battery statistics")
check('"charging"' in measurement and '"discharging"' in measurement and '"status_code"' in measurement,
      "battery charging/discharging status is recorded with the raw platform code")
check('time.monotonic()' in measurement and 'No endurance projection is calculated' in measurement,
      "tool records actual elapsed time without inventing an endurance projection")
check('snapshot()' in client and 'setConnectTimeout(2300)' in client and 'setReadTimeout(2800)' in client,
      "Kodi request timeout behavior remains unchanged")
print("All OS battery source-contract checks passed; they do not replace runtime or endurance testing.")
