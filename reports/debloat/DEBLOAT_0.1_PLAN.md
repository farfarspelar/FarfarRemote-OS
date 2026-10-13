# FarfarRemote OS Debloat 0.1 — package evidence and round plan

**Device:** Sony E2003, Android audit captured 2026-10-13. **State:** plan only; no package was changed. The actual package-by-package ledger is generated in the local audit folder as `package_review.md` and `.csv`.

## Evidence from the captured device

The audit shows 280 packages, Android reporting 918,424 kB RAM, 521,212 kB free and 354,867 kB used at that instant. `dumpsys meminfo` splits PSS into 112,640 kB persistent, 12,733 foreground, 45,968 visible, 35,963 perceptible, 20,705 A Services, 77,701 B Services, 279,728 cached and 16,237 native. Cached PSS can be reclaimed already; it is not a promise that disabling apps will increase free memory by the same amount.

## OS-track checkpoint after v0.4.2-rc1

A read-only ADB check during the 2026-10-13 UTC / 2026-10-14 local checkpoint reconfirmed the exact E2003 / Android 4.4.4 / API 19 / firmware 25.0.A.2.31 target. `org.farfarremote` v0.4.2-rc1 (versionCode 6, target API 28) was installed and its `MainActivity` was foreground; Wi-Fi was connected and the device was USB-powered. No package was disabled and no system setting was changed.

A local provisional measurement was collected to exercise the Phase A metrics path. It reported 918,424 kB total RAM, 462,403 kB free, 363,759 kB used, 330,515 kB active PSS, 160,979 kB cached PSS, and 15.95% CPU busy across a 20-second sample. It was taken immediately after ADB inspection, without the prescribed five-minute settling period, and the App flavor was also installed/running in the captured process list. Treat it as a tooling/diagnostic snapshot, not an OS-only before measurement. No cold-boot time has been recorded. Per-device metrics and raw logs remain local and are excluded from Git.

The live `pm list packages` check confirmed all seven Phase A candidates are installed and enabled, including the proposed first batch: `app.gpsme`, `com.facebook.katana`, `com.mobisystems.office`, `com.navigon.navigator_select_sony_eu`, and `com.scee.psxandroid`. Although Android 4.4 advertises `pm disable-user` and `pm enable --user`, a runtime attempt on this exact firmware returned `SecurityException: Permission Denial` from the ADB shell UID. `app.gpsme` remained enabled, and the script stopped before attempting another package. No package was disabled. Do not retry Phase A through ADB on this firmware unless a separately verified, authorized method is available; root, uninstall and system changes are outside this approval.

A valid OS-only baseline was captured at `20261013T222544Z_baseline` after five minutes idle with the App flavor stopped, OS launcher foreground, Wi-Fi connected and USB power attached. The snapshot reports 329,140 kB active PSS, 179,974 kB cached PSS, 507,918 kB free RAM, 362,684 kB used RAM, and 0.02% CPU busy across the sampling window. This baseline is valid for a future comparison under matching conditions; no before/after improvement can be claimed because the package actions did not occur. The measurement helper rejects a capture while `org.farfarremote.app` is running.

Large observed process groups:

| Process/package | PSS and state | Meaning |
|---|---:|---|
| Google Play Services (`com.google.android.gms`) | 43,785 kB persistent + 52,322 kB cached | Active fused-location, GCM, measurement and API-broker services are listed in `activity_services.txt`; Maps and GPSME bind into GMS. High-risk Phase D only. |
| Shared Google process (`com.google.process.gapps`) | 16,864 kB active | Shared UID process lists GMS, GSF, GSF login and Contacts sync; cannot correctly assign PSS to one package. |
| Google Maps | 56,182 kB cached | Reclaimable process at capture; not 56 MB guaranteed RAM improvement. Phase B. |
| Google Play Store | 38,719 kB cached | App-store UI; retain Android PackageInstaller and ADB install path. Phase B. |
| Google Search/Now | 37,014 kB active, B Services | Background search process. Phase B. |
| Google+ | 21,395 kB cached | Social UI, not controller function. Phase B. |
| Google Talk/Hangouts | 13,795 kB active, A Services | Messaging/account service. Phase B. |
| Sony keyboard | 34,369 kB active, Perceptible | Keep: the settings fallback needs a working text input method for SSID/password and Kodi address entry. |
| Sony HOME | 23,647 kB cached | Keep as crash/fallback launcher in 0.1. `TeleService` declares Sony HOME resource-provider library use. |
| Sony Music | 23,019 kB cached across UI/service; an active route service is recorded | Phase C, with audio/volume and Bluetooth regression. |
| GPSME | 13,741 kB cached; top RSS 43,852 kB | User-installed navigation app; broad GPS/SMS/contact/boot permissions and a GMS measurement binding. Phase A. |
| Sony camera common | 5,579 kB persistent | Keep the framework; Phase C disables only camera-facing clients/add-ons. |
| Sony UserDataLogging | 5,101 kB B Services | Phase D review; not included in early rounds. |

`top.txt` is one CPU snapshot, not a meaningful average. `boot_events.txt` has an `enable_screen` event but no paired boot-start marker; the audit cannot provide a reliable cold-start duration. Both require a new controlled before/after capture, with cold boot timed by stopwatch. No performance gain is claimed yet.

## Dependency decisions

- Keep `com.android.settings`, SettingsProvider, SystemUI, Sony HOME and its overlay, Sony keyboard, `com.android.shell`, PackageInstaller, input devices, TouchFilter, storage/download/media providers, Wi-Fi/connectivity services, Android and MediaTek Bluetooth, SuperStamina, CameraCommon, telephony service/provider and OEM crypto/DRM services.
- `com.sonymobile.superstamina` actively publishes the `xperia_power_service` binder. Do not disable it without power-management/charging analysis.
- `com.android.phone` is persistent, has radio UID 1001 and shares `android.uid.phone` with the telephony provider. `service list` includes phone, phoneEx, SMS and SIM phonebook binders. Keep both through 0.1 even with no SIM use.
- Google Play Services is not used by FarfarRemote, but its active service bindings make the framework a separate high-risk experiment after the user-facing apps. GPSME is a GMS client; remove GPSME first. GMS/GSF and the fused provider are marked `REVIEW`, never bundled into low-risk phase B.
- Keep Sony HOME, Settings, keyboard and ADB paths during this first project release. Immersive mode is not treated as a reliable recovery UI.
- Android 4.4 device identity, `pm disable-user` command and `pm enable` restoration must be checked at runtime by scripts. If the package manager lacks `disable-user`, the script aborts before changes.

## Phases and gate

Candidates and evidence are in `tools/debloat_packages.tsv`; only that explicit file is actionable. Each run processes at most five packages, then requires all regression checks before the next round. All actions use `pm disable-user --user 0`, never `pm uninstall` or root.

| Phase | Contents | Current gate |
|---|---|---|
| A | Third-party navigation/social/office/game/antivirus apps (including GPSME) | Lowest-risk first; up to five packages per round. |
| B | User-facing Google apps, Chrome and Play Store | Keep GMS/GSF, account/login, setup/config, backup and sync core in D. Confirm ADB APK install before disabling Play Store. |
| C | Sony camera clients/add-ons, widgets, media/content applications, screensavers and optional share clients | Do not disable HOME, keyboard, CameraCommon, autopairing or small-app framework. |
| D | Google frameworks, fused location, account/sync providers, messaging/calendar clients and system diagnostics | `REVIEW` only; needs `--allow-reviewed`, typed confirmation and passing A/B/C. `NEVER` rows are hard excluded. Telephony, power, input, system UI, shell and installation stay protected. |

**Recommended first system trial after FarfarRemote 0.2 is verified:** Phase A, default batch size 5, in this order: `app.gpsme`, `com.facebook.katana`, `com.mobisystems.office`, `com.navigon.navigator_select_sony_eu`, `com.scee.psxandroid`. These are installed user applications, not Wi-Fi/input/ADB/launcher framework packages. The 0.2 app uses Android's existing network, input, haptics and HOME contracts; none of those APIs require these five packages. Keep the full regression gate (especially Wi-Fi text entry, touch/buttons, Kodi, Bluetooth if used, USB ADB and `adb install -r`) after the batch. Do not continue to A's last two candidates until the first batch has passed and been measured.

The script requires a captured baseline, exactly one authorized ADB device matching audit serial and E2003 properties, a separate approval flag plus the exact typed confirmation, and status verification after every package. It records all state transitions and stops on ADB loss or an unverified state. On a regression failure it attempts to re-enable only packages this script logged as disabled in that round.

## Execution and tests

1. Collect the matched baseline with the screen, Wi-Fi, charger and Kodi status in the intended steady state:

   ```sh
   ./tools/debloat.sh --measure baseline
   ./tools/debloat.sh --record-boot-seconds baseline 72.4
   ./tools/debloat.sh --phase A
   ```

2. Review the five-package round. Apply one round only after a separate approval:

   ```sh
   ./tools/debloat.sh --phase A --apply --approve-phase A
   ```

   Type the exact prompt text. Script asks for PASS/FAIL on FarfarRemote/HOME, Kodi commands, Wi-Fi/settings text input, touch/physical buttons, charging/power, Bluetooth (N/A only if unused), and ADB plus `adb install -r dist/FarfarRemote-0.2.0-api19-debug.apk`. Install/launch test can be performed in another terminal while the script awaits results.

3. If all checks pass, let the device settle in a fixed idle state, cold boot it manually, test it again, then measure:

   ```sh
   ./tools/debloat.sh --measure after-A
   ./tools/debloat.sh --record-boot-seconds after-A 68.1
   ./tools/analyze_debloat_metrics.py reports/debloat/<adb-serial> --before <baseline-snapshot-name> --after <after-A-snapshot-name>
   ```

   Repeat the same process for every round. Phase B cannot start until all A candidates have been handled and every A round passed. Then use B, C and only if desired D.

4. To restore the last script-owned changes in a phase, inspect first and explicitly apply:

   ```sh
   ./tools/restore.sh --group A
   ./tools/restore.sh --group A --apply --approve
   ```

   Enter `RESTORE E2003 GROUP A`. To restore all script-owned changes use `--group ALL`. The original state is tracked in the local `reports/debloat/<adb-serial>/actions.tsv`; unrelated disabled packages are not touched.

## Measurement rules

Each snapshot stores `dumpsys meminfo`, `/proc/meminfo`, process list, five `top` samples, five `/proc/stat` samples, battery, Wi-Fi, connectivity, uptime and boot events. `analyze_debloat_metrics.py` reports cached PSS separately from active PSS and calculates CPU busy percentage across the sampling window. Compare after the same warm-idle interval, screen state, charger, network, temperature and Kodi availability. Time from physical power-on to the first usable FarfarRemote screen with a stopwatch; the captured audit alone cannot measure boot duration.

Keep the test outcome and package action ledger. An improvement is accepted only when the before/after metrics and regression checks support it; package count is not a success metric.
