# E2003 partition layout — read-only metadata

**Status key:** VERIFIED = directly observed/documented; REPORTED = owner statement; UNKNOWN = insufficient evidence; BLOCKED = cannot continue until named evidence is available.

Captured from the connected Sony E2003 by listing `/dev/block/platform/mtk-msdc.0/by-name` and `/proc/partitions`. The mapping and sizes were rechecked over ADB on 2026-10-14. No partition data was read. `/system` is mounted read-only. The `boot` block node is `root:system` mode `0640`, and a one-byte attempt to read it as shell UID 2000 was denied by permissions; it did not write data. ADB properties independently reported model E2003/build `25.0.A.2.31`, customization `1293-7358` revision `R7A`, and software base `1292-0502` variant `GENERICSS`.

**REPORTED:** the owner says the bootloader is unlocked. **UNKNOWN:** whether `fotakernel` is used as recovery on this installed firmware. **BLOCKED:** image extraction and recovery validation until an exact stock image is obtained.

Sizes below come from `/proc/partitions` in 1-KiB blocks. They are device-reported sizes, not flash instructions. `mmcblk0boot0`, `boot1`, RPMB and raw partition content were not accessed.

| Label | Block node | 1-KiB blocks | Notes |
|---|---:|---:|---|
| ta | mmcblk0p1 | 2,048 | Protected Sony trust/identity area; never alter |
| proinfo | mmcblk0p2 | 3,072 | Protected device information; never alter |
| nvram | mmcblk0p3 | 5,120 | Calibration/radio-sensitive; never alter |
| protect1 | mmcblk0p4 | 10,240 | Protected; never alter |
| protect2 | mmcblk0p5 | 10,240 | Protected; never alter |
| seccfg | mmcblk0p6 | 512 | Security configuration; never alter |
| lk | mmcblk0p7 | 1,024 | Low-level bootloader stage; never alter |
| ltalabel | mmcblk0p8 | 16,384 | Purpose not established |
| fotakernel | mmcblk0p9 | 32,768 | Sony FOTA/recovery-named partition; recovery use not verified |
| boot | mmcblk0p10 | 32,768 | Live raw contents inaccessible to ADB shell; an unmatched E2003 R10A mirror candidate's Sony ELF payload has been inspected offline |
| secro | mmcblk0p11 | 6,144 | Protected security data; never alter |
| para | mmcblk0p12 | 512 | Purpose not established |
| logo | mmcblk0p13 | 8,192 | Boot logo candidate; purpose inferred from name |
| expdb | mmcblk0p14 | 10,240 | Exception/debug logs candidate; purpose not established |
| tee1 | mmcblk0p15 | 5,120 | Trusted execution environment; never alter |
| tee2 | mmcblk0p16 | 5,120 | Trusted execution environment; never alter |
| metadata | mmcblk0p17 | 32,768 | Purpose not established |
| apps_log | mmcblk0p18 | 8,192 | Purpose inferred from name |
| system | mmcblk0p19 | 2,048,000 | Mounted `/system`, ext4, read-only |
| cache | mmcblk0p20 | 204,800 | Mounted `/cache` |
| userdata | mmcblk0p21 | 5,168,640 | Mounted `/data` |
| flashinfo | mmcblk0p22 | 16,384 | Purpose not established |

No standalone `recovery` label appeared. Sony's `fotakernel` convention is a plausible recovery location, but that is an inference only. The bootloader may expose additional vendor-specific modes or write rules; none were tested. The bootloader's accepted image type, partition aliases, signatures and rollback behavior remain **UNKNOWN**.

**Hard boundary:** do not read/write raw protected areas or use scatter/preloader tools. This table is for identification, not authorization to access any block node. Root, repartitioning, flashing and recovery installation are outside this research task.
