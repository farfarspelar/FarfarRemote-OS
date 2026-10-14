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
| Android File Host listing | Lists `E2003_25.0.A.2.31_R3A_E2003_Customized DE_1294-2854.ftf` (~1.2 GB) | **REPORTED unverified mirror**; CDA 1294-2854 differs from live 1293-7358 R7A and listing provides only MD5. Not approved as restore base. |
| Community firmware index | Names `E2003-25.0.A.2.31-R10A-Customized-UK.ftf` | **REPORTED unverified**; no cryptographic checksum and no verified relationship to live CDA. Not approved as restore base. |

Primary/official links: [Sony user guide](https://www-support-downloads.sonymobile.com/e2003/userguide_EN_E2003-E2006-E2053_2_Android4.4.4.pdf), [Sony Xperia Companion](https://www.sony.com/electronics/support/mobile-phones-tablets-tablets/articles/00236877), [Sony Open Devices](https://developer.sony.com/open-source/aosp-on-xperia-open-devices/), [Sony developer repositories](https://github.com/sonyxperiadev), [Sony kernel-copyleft](https://github.com/sonyxperiadev/kernel-copyleft), [Flashtool Linux downloads](https://www.flashtool.net/download.html), [community firmware listing](https://androidfilehost.com/?flid=212192&w=files).

## Extraction workflow (offline only)

1. Record where the FTF came from, exact URL/account/date, file size, archive listing and SHA-256. Do not place firmware/vendor binaries in public Git.
2. Run `research/custom-rom/tools/inspect_ftf.sh FILE.ftf [expected-sha256]`. This checks the ZIP container and lists entries; it does not flash or extract the archive.
3. Use an audited Sony SIN extractor/Flashtool version to extract image payloads to a separate local directory. Record tool version/hash and all output hashes. FTF is a Sony container (commonly ZIP with SIN files); not every SIN type is supported by every tool version.
4. Extract `kernel.sin`/boot payload and system image, then inspect boot metadata using a trusted host-side boot-image parser. Do not patch/repack until the stock image is understood.
5. Verify model/build/CDA by firmware metadata inside the package and compare with live device properties. Filename alone is not evidence.
6. Check whether extracted package includes `boot`, `fotakernel`, `system`, loader and any TA/security-critical data. Do not publish copyrighted images or vendor blobs.

Sony Companion software repair is a possible official recovery service but may choose current or server-available firmware and may wipe user data. It has not been tested on this E2003. Treat the only exact restore candidate as **BLOCKED** until a matching package and end-to-end recovery route are established.
