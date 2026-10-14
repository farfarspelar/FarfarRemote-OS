# Root method assessment — exact E2003 target

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner/community statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

Target: Sony Xperia E4g E2003, Android 4.4.4/API 19, firmware 25.0.A.2.31, customization 1293-7358 R7A.

## Current state

- **VERIFIED:** Live ADB shell is UID 2000 (`shell`), SELinux `u:r:shell:s0`; `/system` is read-only; `su` was not found on the standard shell PATH in the prior readiness check; reading the boot block is denied.
- **VERIFIED, read-only ADB recheck 2026-10-14:** the connected device identifies as E2003; fingerprint is `Sony/E2003/E2003:4.4.4/25.0.A.2.31/4Pf_Nw:user/release-keys`; CDA/revision are `1293-7358 R7A`; API 19. Shell remains UID 2000, no `su` is on PATH or at the standard `/system/bin` and `/system/xbin` paths, and `ro.boot.flash.locked` / `ro.boot.verifiedbootstate` return empty. This confirms neither root nor lock state. No partition data was read or written. Fastboot mode was not entered in this check.
- **REPORTED:** Owner states bootloader is unlocked.
- **UNKNOWN, Fastboot read-only recheck 2026-10-14:** product is E2003, but `getvar unlocked` is blank, `flashing get_unlock_ability` returns `unknown command`, and prior `oem device-info` was unsupported. Thus neither unlocked state nor unlock eligibility can be established through this bootloader's exposed query interface. The phone was returned to Android and its original fingerprint/CDA verified. `ro.bootloader=s1` does not establish lock state.
- **REPORTED, community corroboration only:** Flashtool logs for E2003 devices using the `S1_Root_bee6` / `S1_Boot_MT6732_TC9PRA_9` family show `Bootloader status: ROOTABLE`; another historical E2003 log reports `ROOTED` on build `25.0.A.1.42` ([4PDA E4g log](https://4pda.to/forum/index.php?showtopic=668811&st=100), [Flashtool log](https://forum.android.com.pl/topic/250422-problemy-z-wgraniem-systemu-za-pomoc%C4%85-flastool-a-w%C4%85tek-zbiorczy)). These are community logs for other units/builds, with ambiguous terminology and no reproducible steps. They support platform-level plausibility only; they do not prove this R7A phone is bootloader-unlocked or rooted.
- **VERIFIED:** Owner's application/OS feature report says Wi-Fi reconnects after reboot and FarfarRemote works as HOME; these are the required rollback acceptance checks if a future root experiment is explicitly authorized.

## Candidate methods

| Method | Status for this exact E2003/firmware | Assessment |
|---|---|---|
| Magisk boot-image patch, historical compatible line | **Plausible, unverified** | Magisk v18.1 documents Android 4.2 support, and v16.1 includes MTK boot packaging fixes; v22.1 is the last pre-5.0 release line. Needs exact stock boot, image parse, verified write/restore route, and SELinux/init compatibility. |
| Custom recovery + root ZIP | **Historical E2003 recovery artifact retrieved; R7A behavior unverified** | The archived 2016 XDA post explicitly identifies E2003 and claims the recovery was tested. Its linked TWRP 2.8.7.0 image was retrieved and hashed; embedded identity is E2003/25.0.A.2.31 but customization R5A. Its kernel matches the R10A stock candidate and fstab uses p9, matching live `fotakernel`. No source/build recipe, trusted checksum, independent test, exact restore route or R7A validation exists. See [RECOVERY_STRATEGY.md](RECOVERY_STRATEGY.md). |
| KingRoot | **Historical success claim on the exact Android build, but ambiguous evidence** | A February 2016 E2003 owner reports that a newly found KingRoot APK/database rooted the phone after Sony repair installed `25.0.A.2.31`. In the same discussion, the owner says it had been rooted before that repair; another participant specifically asks whether residual root files explain success. The APK, version, hash, CDA, logs and clean-stock state are missing. This is a stronger exact-build lead than a generic KitKat claim, but it does not establish reproducibility on this clean `1293-7358 R7A` phone. Do not download/run the old APK or substitute a current binary. |
| KingoRoot | **Historical E2003 reports, firmware/CDA mismatch or unknown** | A Turkish E4g forum post describes a PC KingoRoot flow after installing `25.0.A.1.28`; a separate post in that discussion reports a KingRoot APK on `25.0.A.2.31` (see above). A 4PDA E2003 user later says KingRoot-to-SuperSU had worked for months on `25.0.A.2.31`, but gives no initial root method, APK identity, CDA or clean-stock state. Product names are often used inconsistently in forum posts. None establishes a reproducible, trusted exact-R7A procedure. Do not conflate KingRoot and KingoRoot or execute either tool. |
| SuperSU | **Not a vulnerability/root method by itself** | Historically a superuser manager/payload installed after an exploit or custom recovery. Chain/version and compatibility would need their own verification; not a safe root path by itself. |
| MTK one-click/engineering/preloader utilities | **Unverified and high risk** | Generic MediaTek branding does not prove SoC/revision compatibility. Tools that write preloader, NVRAM, security configuration or scatter-defined partitions are explicitly out of scope. No such utility should be run against the connected device. |
| Generic Android exploit apps (e.g. Towelroot-era techniques) | **No exact match verified** | Requires exact kernel build/vulnerability/preconditions. A matching Android version alone is insufficient. |

Historical discussion: [4PDA E4g firmware/root thread](https://4pda.to/forum/index.php?showtopic=668811), [E4g owner report and follow-up questions about KingRoot on 25.0.A.2.31](https://forum.donanimhaber.com/sony-xperia-e4g-ana-konu-ve-kullanicilar-kulubu--105264065-127), [Turkish E4g forum method discussion](https://forum.donanimhaber.com/sony-xperia-e4g-ana-konu-ve-kullanicilar-kulubu--105264065-127), [E4g-specific TWRP download post](https://dianariyanto.com/twrp-recovery-sony-xperia-e4g/), and [XDA recovery thread](https://xdaforums.com/t/twrp-recovey-sony-xperia-e4g-t3425174/). These are research sources, not instructions or endorsement. The historical XDA recovery binary was downloaded for offline static analysis only; it was not executed, booted or flashed.

Security context: rooting utilities commonly obtain privilege by exploiting device vulnerabilities. Research on commercial root providers documents risks in opaque exploit services ([UC Riverside paper](https://www.cs.ucr.edu/~zhiyunq/pub/ccs15_root_providers.pdf)); Microsoft currently classifies a detected KingRoot sample family as a hack tool ([Microsoft detection entry](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=HackTool%3AAndroidOS%2FKingRoot.AA&ThreatID=2147946797)). A detection label is not proof that every historical sample is malicious, but reinforces that unknown APKs must not be trusted.

## Recommendation

There are two distinct research leads, neither currently safe to execute:

1. **KingRoot/KingoRoot exploit route:** more than one historical E4g report describes successful root around this firmware generation, including an exact `25.0.A.2.31` report. The exact APK/database is unavailable, prior-root state is disputed, and the device CDA is not reported. This makes root technically plausible, not verified or safe. Do not install either opaque tool.
2. **Custom recovery route:** an E2003-specific historical TWRP artifact now exists for static review. The device/build identity, kernel match and partition mapping are strong evidence; source, build provenance, R7A compatibility and rollback safety remain unverified. Do not test it until an exact/official restore route is independently established and separate authorization is given.
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
