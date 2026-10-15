# Known limitations

- The supplied local R10A firmware is an unauthenticated mirror artifact. Its `/system` container is hash-pinned, and live R7A differences are restored, but upstream firmware provenance is not independently authenticated.
- Output is only a raw ext4 `/system` filesystem. It is not a complete ROM or Sony flash package and has no tested installer.
- The system was reconstructed using private device reads; the input dump/metadata are not in Git, so another developer cannot reproduce without owner-supplied matching inputs.
- No matching, final R7A kernel config or fully rebuilt boot image is part of v0.1.
- The current experimental boot container uses an R10A ramdisk whose fstab has `autoformat` on `protect1` and `protect2`. Its trigger behavior is not verified. Do not use this boot candidate for another start attempt as-is; obtain a matching R7A ramdisk or prepare and statically audit a narrowly changed copy first.
- That ramdisk also imports Sony bootstrap actions which invoke `wipedata`/`mr` and start `updatemiscta`. Static inspection finds format/reset code and TA-write API references in the corresponding R7A system binaries, but does not establish their runtime guards. Do not boot this ramdisk until its startup side effects are understood and a test variant is reviewed to avoid unintended TA or protected-partition writes.
- The rebuilt callass kernel's saved output has no `.ko` modules, and the live R7A `/system/lib/modules` directory is empty. This does not prove the kernel's built-in driver set matches the device.
- The HOME role can be offered by the inserted APK, but first-boot default selection is not automated or tested.
- Boot animation is statically validated only; Sony path selection and playback are not device-tested.
- No debloat or battery optimization is included. All system components remain to reduce regressions.
- No recovery path is guaranteed. Owner risk acceptance does not make an image flashable or make unrelated partition writes acceptable.
