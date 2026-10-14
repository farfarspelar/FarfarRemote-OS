# E2003 stock firmware and source research

## Target identity to match

Live device: E2003, Android 4.4.4/API 19, build `25.0.A.2.31`, Sony customization `1293-7358 R7A`. Firmware labels and region/revision matter. An E2003 image with different CDA is a candidate to inspect, not an automatically acceptable restore base.

## Sources and confidence

| Source | Finding | Status |
|---|---|---|
| Sony E4g user guide | Confirms the documented E2003/E2006/E2053 family and Sony Companion software repair procedure | **VERIFIED primary source**; does not promise a specific historical build remains downloadable |
| Sony Xperia Companion | Sony says Software Repair is supported; current desktop versions are Windows/macOS | **VERIFIED official service exists**; whether it can restore E2003 to 25.0.A.2.31 or the exact 1293-7358 customization is **UNKNOWN** |
| Sony Open Devices / Sony GitHub | Sony publishes AOSP configuration/source for selected Xperia devices; no E2003 device tree found in current Sony Open Devices repositories | **VERIFIED absence in searched current listing**, not proof no historical archive exists |
| Sony kernel-copyleft | Sony's organization hosts copyleft kernel source/archive repositories | **VERIFIED source location**; exact branch/archive matching kernel `3.10.48+`, E2003, 25.0.A.2.31 and CDA R7A is **BLOCKED/not found** |
| XperiFirm | Community-maintained tool that queries Sony firmware services; modern availability for old E2003 firmware is uncertain | **REPORTED tool lead**, not an official Sony recovery guarantee. Obtain tool from its developer's recognized distribution and verify hash/signature. |
| Flashtool | Linux build 0.9.36.0 is listed by the project with a published SHA-1; can process Sony FTF/SIN formats on some releases | **REPORTED tool lead**. Its old SHA-1 is not a modern authenticity guarantee; test offline against a copy only and inspect current SIN support. |
| AZROM firmware index | Lists `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` under E2003. The `E2003` model and `25.0.A.2.31` build text match; CDA and package contents were not stated on the listing. | **REPORTED, unverified mirror lead**; locally inspected as detailed below, but no trusted SHA-256 or direct Sony provenance. Not approved as a restore image. |
| AZROM E2006 listing | Lists `E2006-25.0.A.2.31-R7A-Nextel-PE.ftf` under the E2006 section. | **VERIFIED listing association, wrong model**. Explicitly exclude from E2003 work despite matching firmware/R7A text. |
| Android File Host listing | Lists `E2003_25.0.A.2.31_R3A_E2003_Customized DE_1294-2854.ftf` (~1.2 GB) | **REPORTED unverified mirror**; CDA 1294-2854 differs from live 1293-7358 R7A and listing provides only MD5. Not approved as restore base. |
| XperiaStockROM mirror listing | Lists `Sony_Xperia_E4G_E2003_25.0.A.2.31_1293-9486_Customized_MEA` (1.3 GB) | **REPORTED unverified mirror**; same marketed model/build but CDA 1293-9486 differs from live 1293-7358 R7A. The site provides no independently trusted checksum or Sony provenance. Not approved as restore base. |
| Community firmware index | Names `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` | **REPORTED unverified**; no cryptographic checksum and no verified relationship to live CDA. Not approved as restore base. |

Primary/official links: [Sony user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf), [Sony Xperia Companion repair information](https://www.sony.com/electronics/support/mobile-phones-tablets-tablets/articles/00236877), [Sony Open Devices](https://developer.sony.com/open-source/aosp-on-xperia-open-devices/), [Sony developer repositories](https://github.com/sonyxperiadev), [Sony kernel-copyleft](https://github.com/sonyxperiadev/kernel-copyleft), [Flashtool Linux downloads](https://www.flashtool.net/download.html). Community leads: [AZROM E4g firmware index](https://azrom.net/rom-sony-xperia-e4g-e2003-e2006-e2053-ftf-firmware-lock-remove-file/), [Android File Host E4g listing](https://androidfilehost.com/?flid=212192&w=files), [UK firmware listing discussion](https://www.martview-forum.com/threads/sony-flash-tool-all-version-firmware-ftf-lock-remove-file.23366/page-2).

## Search update — 2026-10-14

The detail page places `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` in the E2003 section, but places `E2006-25.0.A.2.31-R7A-Nextel-PE.ftf` in the E2006 section. An earlier search-result snippet conflated these entries; it was wrong, and the E2006 file is excluded. The E2003 R10A and AFH R3A/1294-2854 files remain unverified community candidates, not restore images. Neither demonstrates a match to the connected phone's `1293-7358 R7A`. Sony's current repair-service page describes Software Repair, but does not confirm that this retired model/build is still served. Community reports say E4g was removed from recent XperiFirm catalog access; that report is not an official Sony compatibility statement. No candidate is therefore cleared for restoration or flashing.

Sony's official product information continues to identify the marketed E4g E2003 processor as MT6732, while the connected firmware reports the MT6752 platform string. A Sony community discussion also notes the historical MT6732/MT6752 naming confusion, but does not replace exact board/kernel source verification. Do not use generic MT6732/MT6752 kernel repositories as proof of E2003 compatibility.

## Offline inspection of the E2003 R10A candidate — 2026-10-14

The AZROM-listed Google Drive object was downloaded only to `/tmp` for archive inspection. It is **not in Git** and must not be flashed or treated as a restore package.

| Check | Result |
|---|---|
| Filename | `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` |
| Size | 1,304,399,035 bytes |
| SHA-256 observed locally | `ffb5b42cc196eea4d6651817992bf230a3efdbef1e50ac68eb93866aeec8f37b` |
| Provenance | AZROM page points to Google Drive; no independent trusted checksum or Sony signature validation was established |
| ZIP integrity | `unzip -t` completed without compressed-data errors |
| Internal manifest | `device: E2003`; `version: 25.0.A.2.31_R10A`; `branding: CustomizedUK`; `cda:` and `revision:` are blank |
| Match to installed phone | **Not established**: live device is CDA/customization `1293-7358 R7A`; candidate has no CDA/revision in its manifest |
| Contents | Includes `boot.sin`, `fotakernel.sin`, `system.sin`, `preloader_s1sbl.sin`, `secro.sin`, `tee1.sin`, `tee2.sin`, TA files and other firmware partitions |

The FTF's `default.fsc` contains operations for critical boot/security partitions and TA data. Do not use the FTF as a bundle or feed it to a flashing workflow. Its archive integrity proves only that the downloaded ZIP data is internally consistent; it does **not** authenticate the mirror, establish a correct CDA match, or demonstrate that it can restore this handset.

### Boot and FOTA payload inspection

Only `boot.sin` and `fotakernel.sin` were extracted into `/tmp/farfar-e2003-sin-inspect`. Their SIN v3 MMCF/ADDR payload SHA-256 digests matched the hashes embedded in each file. Both decoded payloads are ARM ELF executables. ELF program headers show a first segment containing the same gzip-compressed kernel in both images and a second segment containing different gzip-compressed root filesystems. The first-segment decompressed bytes contain the kernel string `Linux version 3.10.48+ ... gcc 4.8 ... Tue Sep 8 11:03:22 CST 2015`.

The boot ramdisk's read-only cpio listing includes Android `init`, `init.mt6752.rc`, `fstab`, `adbd`, and Sony/MediaTek startup scripts. Its fstab mounts `/system` read-only and `/data`, `/cache`, `/protect1`, `/protect2`; the project init script creates MediaTek WMT/Wi-Fi/Bluetooth device nodes and starts connectivity services. Its `default.prop` says `ro.semc.version.sw=1292-0502`, `ro.semc.version.sw_variant=GENERICSS`, `ro.secure=1`, and `ro.debuggable=0`; this is not the live phone's `1293-7358 R7A` identity. This is evidence of the image's intended stack, not proof that this R10A image is interchangeable with the installed R7A image. The `fotakernel` ramdisk is a FOTA-oriented environment and is not validated as a usable recovery.

The SIN parser reference was the read-only v3 implementation in [Androxyde/Flashtool](https://github.com/Androxyde/Flashtool/tree/master/Flashtool/src/main/java/org/flashtool/parsers/sin/v3), checked out at commit `7529dce9a1ffb81e365ba1d7e15f6773463ffd7a`. The repository now includes `tools/extract_e2003_boot_payloads.py`, a bounded standard-library reader for only the two named SIN entries. It refuses non-E2003 manifests, requires a new output directory, verifies SHA-256 payload records and emits only 32-bit ARM ELF images. The general `j4nn/sinunpack` executable was not used because its main program scans all SINs and includes USB/flashing code. Extracted firmware and payloads remain outside the repository. Example: `python3 research/custom-rom/tools/extract_e2003_boot_payloads.py /absolute/path/to/E2003.ftf /tmp/e2003-boot-analysis`.

### Kernel source search

The public Sony [`kernel-copyleft`](https://github.com/sonyxperiadev/kernel-copyleft) repository was checked through its current remote branch refs. It exposes older `14.1.*` and later Xperia kernel release branches, but no `25.0.A.*` branch or E2003/MT6752-specific source branch was found. Sony's current Open Devices device list likewise does not identify E2003. This is a **bounded negative search**, not proof Sony never published a standalone archive elsewhere. No `callass` defconfig or matching kernel source revision has been located. The extracted kernel does not contain the `IKCFG_ST`/`IKCFG_ED` markers for an embedded config.

**Conclusion:** We now have a useful E2003/build-labelled *offline analysis candidate*, not an authenticated exact restore base. Exact installed customization remains unmatched. The next safe work is to compare relevant image/ramdisk properties and obtain the exact 1293-7358 R7A package or an independently verified official Sony repair path.

## Extraction workflow (offline only)

1. Record where the FTF came from, exact URL/account/date, file size, archive listing and SHA-256. Do not place firmware/vendor binaries in public Git.
2. Run `research/custom-rom/tools/inspect_ftf.sh FILE.ftf [expected-sha256]`. This checks the ZIP container and lists entries; it does not flash or extract the archive.
3. Use an audited Sony SIN extractor/Flashtool version to extract image payloads to a separate local directory. Record tool version/hash and all output hashes. FTF is a Sony container (commonly ZIP with SIN files); not every SIN type is supported by every tool version.
4. Extract `kernel.sin`/boot payload and system image, then inspect boot metadata using a trusted host-side boot-image parser. Do not patch/repack until the stock image is understood.
5. Verify model/build/CDA by firmware metadata inside the package and compare with live device properties. Filename alone is not evidence.
6. Check whether extracted package includes `boot`, `fotakernel`, `system`, loader and any TA/security-critical data. Do not publish copyrighted images or vendor blobs.

Sony Companion software repair is a possible official recovery service but may choose current or server-available firmware and may wipe user data. It has not been tested on this E2003. Treat the only exact restore candidate as **BLOCKED** until a matching package and end-to-end recovery route are established.
