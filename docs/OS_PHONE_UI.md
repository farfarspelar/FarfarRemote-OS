# FarfarRemote OS Phone UI Suppression

## Scope

The Xperia still runs Sony's Android 4.4.4 framework. Its `com.android.phone` package posts a **No SIM card** notification, confirmed on the connected E2003. The dedicated HOME launcher hides the normal phone launcher UI during regular use, but the Android notification shade remains accessible.

FarfarRemote OS now contains an optional OS-flavor-only notification listener. When the owner enables it in Android's Notification Access settings, it dismisses only notifications from `com.android.phone` whose text explicitly says `No SIM` / `No-SIM`. It does not disable, uninstall, or modify telephony services or packages. The normal App flavor does not declare this listener.

## Enable or disable

Open FarfarRemote Settings → System Information → **Enable phone alert filter**. On Android 5.1 and newer, Android opens Notification Access settings; enable or disable **FarfarRemote phone alert filter** there. On Xperia's Android 4.4, the button opens Android Settings; navigate to **Security → Notification access** and enable or disable FarfarRemote. The setting is controlled by Android and can be revoked at any time. Reopen FarfarRemote Settings after returning to refresh the displayed state.

Notification Access is a user-granted Android capability. The filter cannot remove the already-posted alert until the service binds; after granting access, dismiss the existing alert once if it remains visible. Future matching no-SIM alerts are dismissed automatically.

## Known limitation

This filter only handles the specific `com.android.phone` no-SIM notification. It does not change the `Emergency calls only` network-state label that Sony's System UI may show in the shade/status area. Removing that label would require a separate Sony SystemUI/framework change and device testing. Phone packages, emergency-call support, Wi-Fi, and telephony framework services remain intact.

No system image was changed or installed as part of this implementation.
