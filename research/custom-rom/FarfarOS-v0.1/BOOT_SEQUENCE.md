# Boot sequence and branding

## Expected stock sequence

Power button → Sony boot ROM / bootloader → Sony kernel and init ramdisk → Android init and vendor services → Android framework/System Server → boot-animation service → Wi-Fi and connectivity services → HOME resolution → FarfarRemote OS.

The stock system image uses `/system/bin/bootanimation`; read-only inspection found strings for `/system/media/bootanimation.zip` and Sony fallback locations. The animation archive is 540×960 at 18 fps, with a one-shot `part0` intro and looping `part1`. The build script replaces only `/system/media/bootanimation.zip` in the offline system image, preserving its R7A owner, mode, and SELinux label.

## Limits

The animation has not been played by a booted experimental image. Sony's path precedence and actual end-to-end timing are not verified. No bootloader splash/logo partition is altered. Default HOME selection may be shown by Android on first boot; automatic default-app provisioning has not been proven and must not be claimed. Existing Sony startup services and phone warnings remain in this first image.
