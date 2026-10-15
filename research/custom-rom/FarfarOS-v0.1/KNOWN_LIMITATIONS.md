# Known limitations

- The supplied local R10A firmware is an unauthenticated mirror artifact. Its `/system` container is hash-pinned, and live R7A differences are restored, but upstream firmware provenance is not independently authenticated.
- Output is only a raw ext4 `/system` filesystem. It is not a complete ROM or Sony flash package and has no tested installer.
- The system was reconstructed using private device reads; the input dump/metadata are not in Git, so another developer cannot reproduce without owner-supplied matching inputs.
- No matching, final R7A kernel config or fully rebuilt boot image is part of v0.1.
- The HOME role can be offered by the inserted APK, but first-boot default selection is not automated or tested.
- Boot animation is statically validated only; Sony path selection and playback are not device-tested.
- No debloat or battery optimization is included. All system components remain to reduce regressions.
- No recovery path is guaranteed. Owner risk acceptance does not make an image flashable or make unrelated partition writes acceptable.
