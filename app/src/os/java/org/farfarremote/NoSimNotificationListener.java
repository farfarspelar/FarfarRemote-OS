package org.farfarremote;

import android.app.Notification;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

/** Optional OS-flavor-only filter for the stock no-SIM alert; telephony stays enabled. */
public final class NoSimNotificationListener extends NotificationListenerService {
    private static final String PHONE_PACKAGE = "com.android.phone";

    @Override public void onListenerConnected() {
        super.onListenerConnected();
        StatusBarNotification[] active = getActiveNotifications();
        if (active == null) return;
        for (StatusBarNotification notification : active) dismissNoSimAlert(notification);
    }

    @Override public void onNotificationPosted(StatusBarNotification notification) {
        dismissNoSimAlert(notification);
    }

    private void dismissNoSimAlert(StatusBarNotification status) {
        if (status == null || !PHONE_PACKAGE.equals(status.getPackageName())) return;
        Notification notification = status.getNotification();
        if (notification == null) return;
        CharSequence title = null, text = null;
        if (notification.extras != null) {
            title = notification.extras.getCharSequence(Notification.EXTRA_TITLE);
            text = notification.extras.getCharSequence(Notification.EXTRA_TEXT);
        }
        String content = (String.valueOf(title) + " " + String.valueOf(text) + " " + String.valueOf(notification.tickerText)).toLowerCase(java.util.Locale.US);
        if (content.contains("no sim") || content.contains("no-sim")) {
            cancelNotification(status.getPackageName(), status.getTag(), status.getId());
        }
    }
}
