# Boot sequence and branding

## Expected stock sequence

Power button → Sony boot ROM / bootloader → Sony kernel and init ramdisk → Android init and vendor services → Android framework/System Server → boot-animation service → Wi-Fi and connectivity services → HOME resolution → FarfarRemote OS.

The stock system image uses `/system/bin/bootanimation`; read-only inspection found strings for `/system/media/bootanimation.zip` and Sony fallback locations. The animation archive is 540×960 at 18 fps, with a one-shot `part0` intro and looping `part1`. The build script replaces only `/system/media/bootanimation.zip` in the offline system image, preserving its R7A owner, mode, and SELinux label.

## HOME selection policy

Android 4.4 includes user-facing settings for choosing the default Home application; the Android 4.4 Compatibility Definition requires a corresponding settings menu. FarfarRemote's APK exposes the HOME intent, so Android can offer it as a launcher. Installing it under `/system/app` does **not** by itself demonstrate that Android will choose it without prompting. For the first experimental boot, use the normal Android launcher chooser/Settings flow and select FarfarRemote as Home. Keep Sony's original launcher installed during the first boot tests so Settings and a fallback Home remain available. Do not pre-seed `/data/system` preference state or add an untested PackageManager preferred-activity file: that risks hidden precedence and can remove a useful recovery route. Source: [Android 4.4 Compatibility Definition, Default App Settings](https://source.android.com/docs/compatibility/4.4/android-4.4-cdd).

### Live E2003 HOME state (read-only, 2026-10-15)

ADB confirmed the connected device as E2003 / Android 4.4.4 / build `25.0.A.2.31` / CDA `1293-7358 R7A`. `dumpsys package` reports the current preferred HOME activity as `org.farfarremote/.MainActivity`, with `mAlways=true`; the selection record lists both Sony launchers as alternatives. The FarfarRemote package is currently installed from `/data/app` as version `0.4.6-rc5`. This is a direct observation of the live R7A user's state, not a test of the reconstructed system image.

This improves the first-boot plan: preserving `/data` should preserve the existing HOME preference and app data, subject to Package Manager accepting the same package identity/signature when the system copy is introduced. That migration is **not verified**. Do not wipe `/data`; if a system-image experiment resets it, plan to reselect FarfarRemote as Home and re-enter or restore settings. The retained Sony launcher and USB debugging remain fallback access paths for early tests.

## Limits

The animation has not been played by a booted experimental image. Sony's path precedence and actual end-to-end timing are not verified. No bootloader splash/logo partition is altered. HOME registration is statically present in the APK, but the chooser/default-selection behavior has not been tested in this reconstructed image. Existing Sony startup services and phone warnings remain in this first image.
