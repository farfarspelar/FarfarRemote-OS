# System component policy

## Retained in v0.1

The reconstructed `/system` follows the live R7A file manifest and restores the differing payloads from the device capture. The experiment does not delete packages or init services. This preserves the known-good Android framework and vendor integration while ROM boot behavior remains untested.

Keep at minimum:

- Android framework, Package Manager, System Server, System UI, Settings and input method.
- Sony/MediaTek display, gralloc, hwcomposer, touchscreen/input, power, sensors and battery/charger HALs.
- Wi-Fi supplicant/client libraries, DHCP/network stack, netd, firmware/NVRAM calibration references and Sony connectivity services.
- USB/ADB functions, vold/storage, init scripts, SELinux policy, linker configuration and shared libraries.
- Audio policy/HAL and media codecs used by Kodi playback control feedback or future local playback.
- Recovery/boot support files and all R7A-specific configuration.
- FarfarRemote OS as the HOME-capable Android application.

## Deferred candidates

Camera UI, wallpapers/live wallpapers, Sony widgets, social/share apps, Google consumer apps, phone dialer/SMS UI, and update clients could be evaluated for removal only after a complete package/provider/service dependency inventory and boot tests. Their names alone are not proof that libraries, content providers, shared UIDs, overlays or setup flows are unused.

## Explicitly not removed in v0.1

No APK, framework library, provider, daemon, init service, permission XML, overlay, firmware file, or partition is removed or disabled. This is intentionally a minimal-delta system image build. A later debloat phase must use a reviewed allowlist/denylist, preserve Settings/input/network/ADB, and measure each change.
