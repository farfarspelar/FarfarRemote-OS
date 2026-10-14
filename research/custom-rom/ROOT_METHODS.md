# Root method assessment — exact E2003 target

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner/community statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

Target: Sony Xperia E4g E2003, Android 4.4.4/API 19, firmware 25.0.A.2.31, customization 1293-7358 R7A.

## Current state

- **VERIFIED:** Live ADB shell is UID 2000 (`shell`), SELinux `u:r:shell:s0`; `/system` is read-only; `su` was not found on the standard shell PATH in the prior readiness check; reading the boot block is denied.
- **VERIFIED, read-only recheck 2026-10-14:** exact E2003 / `25.0.A.2.31` identity still matches; UID remains 2000 and `su` is absent from PATH. No Fastboot device was attached, so bootloader status was not retested. Package manager reports two disabled entries; their provenance is unknown and no package state was modified.
- **REPORTED:** Owner states bootloader is unlocked.
- **UNKNOWN:** Fastboot's `getvar unlocked` returned no value and `oem device-info` was unsupported. `ro.bootloader=s1` does not establish lock state.
- **VERIFIED:** Owner's application/OS feature report says Wi-Fi reconnects after reboot and FarfarRemote works as HOME; these are the required rollback acceptance checks if a future root experiment is explicitly authorized.

## Candidate methods

| Method | Status for this exact E2003/firmware | Assessment |
|---|---|---|
| Magisk boot-image patch, historical compatible line | **Plausible, unverified** | Magisk v18.1 documents Android 4.2 support, and v16.1 includes MTK boot packaging fixes; v22.1 is the last pre-5.0 release line. Needs exact stock boot, image parse, verified write/restore route, and SELinux/init compatibility. |
| Custom recovery + root ZIP | **Reported only** | Historical E4g TWRP posts exist, but artifacts/build instructions have not been authenticated against E2003 single-SIM 25.0.A.2.31 CDA 1293-7358 R7A. |
| KingRoot | **Reported exact build success; not independently verified** | A February 2016 post in an E4g thread explicitly claims the KingRoot app rooted an E2003 on `25.0.A.2.31`. Other historical posts report failures on nearby E4g builds or name different tools. No trustworthy APK/version/hash, exact CDA, logs, source, or reproducible procedure is provided. This makes exploit-root technically plausible, not safe or verified. Do not download/run the old APK or substitute a current binary. |
| KingoRoot | **Unknown/inapplicable evidence** | Different product from KingRoot. No exact E2003 25.0.A.2.31 method verified. Do not conflate their names or tools. |
| SuperSU | **Not a vulnerability/root method by itself** | Historically a superuser manager/payload installed after an exploit or custom recovery. Chain/version and compatibility would need their own verification; not a safe root path by itself. |
| MTK one-click/engineering/preloader utilities | **Unverified and high risk** | Generic MediaTek branding does not prove SoC/revision compatibility. Tools that write preloader, NVRAM, security configuration or scatter-defined partitions are explicitly out of scope. No such utility should be run against the connected device. |
| Generic Android exploit apps (e.g. Towelroot-era techniques) | **No exact match verified** | Requires exact kernel build/vulnerability/preconditions. A matching Android version alone is insufficient. |

Historical discussion: [4PDA E4g firmware/root thread](https://4pda.to/forum/index.php?showtopic=668811), [Android.com.pl E4g thread with the explicit E2003/25.0.A.2.31 KingRoot claim](https://forum.android.com.pl/topic/242322-root-na-najnowszym-sofcie250a214-dla-xperii-e4g/20), [Kingo compatibility thread](https://4pda.to/forum/index.php?showtopic=503845&st=3000), and [E4g XDA recovery thread link referenced by community discussion](https://xdaforums.com/t/twrp-recovey-sony-xperia-e4g-t3425174/). These are **REPORTED**, not instructions or endorsement. In particular, the forum claim has not been reproduced on this handset and does not identify the exact CDA or tool build.

Security context: rooting utilities commonly obtain privilege by exploiting device vulnerabilities. Research on commercial root providers documents risks in opaque exploit services ([UC Riverside paper](https://www.cs.ucr.edu/~zhiyunq/pub/ccs15_root_providers.pdf)); Microsoft currently classifies a detected KingRoot sample family as a hack tool ([Microsoft detection entry](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=HackTool%3AAndroidOS%2FKingRoot.AA&ThreatID=2147946797)). A detection label is not proof that every historical sample is malicious, but reinforces that unknown APKs must not be trusted.

## Recommendation

There are two distinct research leads, neither currently safe to execute:

1. **KingRoot exploit route:** there is a historical, exact model/build *claim* for E2003/25.0.A.2.31. Because the APK provenance/version and outcome are not reproducible, treat it as a clue for research only. Do not install it.
2. **Magisk patch route:** technically cleaner and auditable if we can obtain the exact stock image and convert Sony's ELF representation without changing its boot semantics. Current extracted image is an unmatched R10A candidate and no standard `boot.img` or verified recovery route exists.

So the answer is: root may well be achievable on this software (the old KingRoot report supports that hypothesis), but an exact, trusted, currently actionable method is **not verified**. Do not execute KingRoot/KingoRoot or proprietary PC tools. Do not unlock, flash, wipe, disable system packages, or write any partition in this phase.

## Minimum evidence before a future root attempt

1. Verify exact device identity, build fingerprint and customization again.
2. Acquire stock firmware from a source with traceable provenance; verify archive integrity and obtain the original boot payload.
3. Confirm exact image is for E2003/25.0.A.2.31 and inspect header/ramdisk locally.
4. Establish exact bootloader state and a model-appropriate stock restore route independently.
5. If considering the historical KingRoot lead, first identify the exact APK/version referenced and establish provenance, hash, behavior and exploit side effects in an isolated analysis environment. If that cannot be done, discard this route and continue with an auditable boot-image method.
6. Rehearse a read-only/dry-run recovery procedure. Document likely data loss and preserve FarfarRemote settings.
7. Obtain separate explicit authorization before any on-device root/flash or reboot-to-bootloader action.
