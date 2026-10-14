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
| Custom recovery + root ZIP | **Reported for E4g family; exact binary unverified** | A 2016 XDA TWRP thread is referenced by E4g forums; later E4g community posts claim TWRP was installed on E2003. A 2017 E4g-specific blog also lists recovery ZIPs, but only through short-link file hosts. No artifact/source/hash has been audited against this phone's `1293-7358 R7A`; another owner reports a recovery-related bootloop. |
| KingRoot | **Historical success claim, ambiguous evidence** | A February 2016 owner post describes obtaining KingRoot on an E2003 after a Sony software repair installed `25.0.A.2.31`, but says the device had been rooted before the repair; a follow-up explicitly questions whether residual root files explain success. It does not prove a clean-stock E2003/R7A method. Other posts name different tools or report failures. No trustworthy APK/version/hash, exact CDA, logs, source, or reproducible procedure is provided. Do not download/run the old APK or substitute a current binary. |
| KingoRoot | **Unknown/inapplicable evidence** | Different product from KingRoot. No exact E2003 25.0.A.2.31 method verified. Do not conflate their names or tools. |
| SuperSU | **Not a vulnerability/root method by itself** | Historically a superuser manager/payload installed after an exploit or custom recovery. Chain/version and compatibility would need their own verification; not a safe root path by itself. |
| MTK one-click/engineering/preloader utilities | **Unverified and high risk** | Generic MediaTek branding does not prove SoC/revision compatibility. Tools that write preloader, NVRAM, security configuration or scatter-defined partitions are explicitly out of scope. No such utility should be run against the connected device. |
| Generic Android exploit apps (e.g. Towelroot-era techniques) | **No exact match verified** | Requires exact kernel build/vulnerability/preconditions. A matching Android version alone is insufficient. |

Historical discussion: [4PDA E4g firmware/root thread](https://4pda.to/forum/index.php?showtopic=668811), [E4g owner report and follow-up questions about KingRoot on 25.0.A.2.31](https://forum.donanimhaber.com/sony-xperia-e4g-ana-konu-ve-kullanicilar-kulubu--105264065-127), [E4g-specific TWRP download post](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/), and [XDA recovery thread](https://xdaforums.com/t/twrp-recovey-sony-xperia-e4g-t3425174/). These are **REPORTED**, not instructions or endorsement. No root/recovery artifact was downloaded or run.

Security context: rooting utilities commonly obtain privilege by exploiting device vulnerabilities. Research on commercial root providers documents risks in opaque exploit services ([UC Riverside paper](https://www.cs.ucr.edu/~zhiyunq/pub/ccs15_root_providers.pdf)); Microsoft currently classifies a detected KingRoot sample family as a hack tool ([Microsoft detection entry](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=HackTool%3AAndroidOS%2FKingRoot.AA&ThreatID=2147946797)). A detection label is not proof that every historical sample is malicious, but reinforces that unknown APKs must not be trusted.

## Recommendation

There are two distinct research leads, neither currently safe to execute:

1. **KingRoot exploit route:** there is a historical E2003/25.0.A.2.31 *claim*, but the poster disclosed prior rooting and another participant questioned residual root state. Treat it as weak evidence only. Do not install it.
2. **Custom recovery route:** E4g-family TWRP is a credible historical lead and appears to have been used on E2003, but files are not currently traceable enough to verify. Obtain the original XDA source/build/artifact and audit it before considering any boot test.
3. **Magisk patch route:** technically cleaner and auditable if we obtain the exact R7A boot image and can convert Sony's ELF representation without changing boot semantics. The local candidate is R10A and no standard `boot.img` or verified restore route exists.

So the answer is: root is **plausible but not yet demonstrated on clean stock for this exact CDA/build**. The weak KingRoot report and historical E4g recovery reports justify continued research, not execution. Do not execute KingRoot/KingoRoot or proprietary PC tools. Do not unlock, flash, wipe, disable system packages, or write any partition in this phase.

## Minimum evidence before a future root attempt

1. Verify exact device identity, build fingerprint and customization again.
2. Acquire stock firmware from a source with traceable provenance; verify archive integrity and obtain the original boot payload.
3. Confirm exact image is for E2003/25.0.A.2.31 and inspect header/ramdisk locally.
4. Establish exact bootloader state and a model-appropriate stock restore route independently.
5. If considering the historical KingRoot lead, first identify the exact APK/version referenced and establish provenance, hash, behavior and exploit side effects in an isolated analysis environment. If that cannot be done, discard this route and continue with an auditable boot-image method.
6. Rehearse a read-only/dry-run recovery procedure. Document likely data loss and preserve FarfarRemote settings.
7. Obtain separate explicit authorization before any on-device root/flash or reboot-to-bootloader action.
