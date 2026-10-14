package org.farfarremote;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Vibrator;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import android.net.Uri;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import java.util.Locale;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Remote UI and input/action layer. Network operations are serialized off the UI thread. */
public final class MainActivity extends Activity {
    private static final String PREFS = "farfarremote"; // Keep 0.1 preference file/key names for upgrade continuity.
    private static final String KODI_HTTP_SERVICE = "_xbmc-jsonrpc-h._tcp.";
    private static final long KODI_DISCOVERY_TIMEOUT_MS = 8000;
    private static final int BG = Color.rgb(7, 15, 27), PANEL = Color.rgb(14, 28, 45), TEXT = Color.rgb(235, 243, 252), MUTED = Color.rgb(154, 177, 202), CYAN = Color.rgb(35, 170, 255), GREEN = Color.rgb(52, 222, 157), RED = Color.rgb(255, 112, 116);
    private static final String COFFEE_URL = "https://buymeacoffee.com/farfarspelar";

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final ExecutorService commands = Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private FrameLayout screen;
    private ScrollView settingsScroll;
    private TextView settingsKodiStatus;
    private int previousSoftInputMode;
    private boolean settingsImeModeSet;
    private boolean inSettings, busy, draggingSeek, destroyed, activityStarted;
    private boolean startupShown;
    private boolean screenIsOn = true;
    private boolean screenReceiverRegistered;
    private int consecutivePollFailures;
    private long lastBatteryInteractionMs;
    private boolean kodiShutdownRequested;
    private boolean connected;
    private volatile int activePlayerId = -1;
    private String currentArtwork = "";
    private Bitmap artwork;
    private NsdManager nsdManager;
    private NsdManager.DiscoveryListener kodiDiscovery;
    private AlertDialog discoveryDialog;
    private final ArrayDeque<NsdServiceInfo> pendingKodiServices = new ArrayDeque<>();
    private final ArrayList<KodiEndpoint> resolvedKodiEndpoints = new ArrayList<>();
    private final Set<String> seenKodiEndpoints = new HashSet<>();
    private boolean resolvingKodiService, kodiDiscoveryTimedOut;
    private Runnable kodiDiscoveryTimeout;
    private EditText discoveryHostField, discoveryPortField, discoveryUsernameField, discoveryPasswordField;
    private Object settingsBackCallback;

    private final BroadcastReceiver screenStateReceiver = new BroadcastReceiver() {
        @Override public void onReceive(Context context, Intent intent) {
            if (intent == null || intent.getAction() == null) return;
            if (Intent.ACTION_SCREEN_OFF.equals(intent.getAction())) {
                screenIsOn = false;
                handler.removeCallbacks(poll);
                android.util.Log.d("FarfarRemoteBattery", "screen_off polling_suspended=true");
            } else if (Intent.ACTION_SCREEN_ON.equals(intent.getAction())) {
                screenIsOn = true;
                lastBatteryInteractionMs = android.os.SystemClock.elapsedRealtime();
                android.util.Log.d("FarfarRemoteBattery", "screen_on polling_resumed=true");
                schedulePoll(0);
            }
        }
    };

    private static final class KodiEndpoint {
        final String name, host, port;
        String state = "Checking…";
        KodiEndpoint(String name, String host, int port) { this.name = name; this.host = host; this.port = String.valueOf(port); }
        String key() { return host + ":" + port; }
        String label() { return name + "\n" + host + ":" + port + " · " + state; }
    }

    /** API 33 back callback isolated so API 19 can still load the Activity. */
    private static final class Api33BackHandler {
        static Object register(Activity activity, Runnable action) {
            android.window.OnBackInvokedCallback callback = action::run;
            activity.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, callback);
            return callback;
        }
        static void unregister(Activity activity, Object callback) {
            if (callback instanceof android.window.OnBackInvokedCallback) {
                activity.getOnBackInvokedDispatcher().unregisterOnBackInvokedCallback(
                        (android.window.OnBackInvokedCallback) callback);
            }
        }
    }

    /** API 35 edge-to-edge APIs are isolated from the API 19 Activity verifier. */
    private static final class Api35WindowInsets {
        static void install(FrameLayout target) {
            target.setOnApplyWindowInsetsListener((view, windowInsets) -> {
                int types = android.view.WindowInsets.Type.systemBars() | android.view.WindowInsets.Type.displayCutout();
                android.graphics.Insets safe = windowInsets.getInsets(types);
                int bottom = safe.bottom;
                if (windowInsets.isVisible(android.view.WindowInsets.Type.ime())) {
                    bottom = Math.max(bottom, windowInsets.getInsets(android.view.WindowInsets.Type.ime()).bottom);
                }
                view.setPadding(safe.left, safe.top, safe.right, bottom);
                return windowInsets;
            });
        }
    }

    private TextView status, hostLabel, titleText, episodeText, elapsedText, durationText, stateText, audioValue, subsValue, connectionNote, settingsFeedback, volumeValue;
    private ImageView poster;
    private SeekBar progress;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        applyOrientationPreference();
        applyKeepAwake();
        applyReducedBrightness();
        if (getResources().getBoolean(R.bool.dedicated_os)) getWindow().getDecorView().setSystemUiVisibility(5894 | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
        buildScreen();
    }

    private void applyOrientationPreference() {
        String mode = prefs.getString("orientation", "portrait");
        if ("landscape".equals(mode)) setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        else if ("auto".equals(mode)) setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR);
        else setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
    }

    private void applyKeepAwake() {
        if (prefs.getBoolean("keep_awake", false)) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    private boolean isDedicatedOs() { return getResources().getBoolean(R.bool.dedicated_os); }

    private ExecutorService userRequestExecutor() { return isDedicatedOs() ? commands : io; }

    private void applyReducedBrightness() {
        WindowManager.LayoutParams attributes = getWindow().getAttributes();
        attributes.screenBrightness = isDedicatedOs() && prefs.getBoolean("os_battery_dim", false) ? 0.25f : WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;
        getWindow().setAttributes(attributes);
    }

    private void noteBatteryInteraction() {
        if (isDedicatedOs()) lastBatteryInteractionMs = android.os.SystemClock.elapsedRealtime();
    }

    @Override public boolean dispatchTouchEvent(MotionEvent event) {
        if (event != null && event.getAction() == MotionEvent.ACTION_DOWN) noteBatteryInteraction();
        return super.dispatchTouchEvent(event);
    }

    private void buildScreen() {
        inSettings = false;
        updateSettingsBackCallback();
        if (settingsImeModeSet) { getWindow().setSoftInputMode(previousSoftInputMode); settingsImeModeSet = false; }
        settingsScroll = null; settingsKodiStatus = null;
        screen = new FrameLayout(this);
        screen.setBackgroundColor(BG);
        configureAppWindowInsets(screen);
        setContentView(screen);
        if (!getResources().getBoolean(R.bool.dedicated_os) && android.os.Build.VERSION.SDK_INT >= 35) screen.requestApplyInsets();
        View content = isLandscape() ? buildLandscape() : buildPortrait();
        screen.addView(content, new FrameLayout.LayoutParams(-1, -1));
        if (!startupShown) { startupShown = true; showStartupOverlay(); }
        setStatus(connected ? "CONNECTED" : "Kodi offline · Settings to configure");
    }

    /** Target 35+ apps draw behind system bars; keep app content inside safe insets. */
    private void configureAppWindowInsets(FrameLayout target) {
        if (getResources().getBoolean(R.bool.dedicated_os) || android.os.Build.VERSION.SDK_INT < 35) return;
        Api35WindowInsets.install(target);
    }

    private void showStartupOverlay() {
        final FrameLayout splash = new FrameLayout(this);
        splash.setBackgroundColor(BG);
        ImageView logo = new ImageView(this); logo.setImageResource(R.drawable.boot_logo); logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(dp(204), dp(204), Gravity.CENTER);
        splash.addView(logo, lp);
        screen.addView(splash, new FrameLayout.LayoutParams(-1, -1));
        splash.getViewTreeObserver().addOnPreDrawListener(new android.view.ViewTreeObserver.OnPreDrawListener() {
            @Override public boolean onPreDraw() {
                splash.getViewTreeObserver().removeOnPreDrawListener(this);
                handler.post(() -> { if (splash.getParent() != null) screen.removeView(splash); });
                return true;
            }
        });
    }

    private boolean isLandscape() { return getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE; }

    private View buildPortrait() {
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true); scroll.setVerticalScrollBarEnabled(false);
        LinearLayout root = column(); root.setPadding(dp(12), dp(8), dp(12), dp(14)); scroll.addView(root);
        addHeader(root);
        addNowPlaying(root, false);
        LinearLayout controls = row(root); controls.setGravity(Gravity.CENTER);
        addIconControl(controls, R.drawable.action_back, "Back", 1f, this::back);
        addIconControl(controls, R.drawable.action_home, "Home", 1f, () -> action(c -> c.call("Input.Home", new JSONObject())));
        addIconControl(controls, R.drawable.action_play_pause, "Play / Pause", 1.12f, this::playPause);
        addIconControl(controls, R.drawable.action_stop, "Stop", 1f, this::stop);
        addIconControl(controls, R.drawable.action_settings, "Settings", 1f, this::showSettings);
        LinearLayout nav = row(root); nav.setGravity(Gravity.CENTER_VERTICAL);
        addDpad(nav, 1.35f);
        addVolume(nav, .52f);
        addTransport(root);
        addCategories(root);
        return scroll;
    }

    private View buildLandscape() {
        ScrollView outer = new ScrollView(this); outer.setFillViewport(true); outer.setVerticalScrollBarEnabled(false);
        LinearLayout root = column(); root.setPadding(dp(12), dp(7), dp(12), dp(10)); outer.addView(root);
        addHeader(root);
        LinearLayout body = row(root); body.setGravity(Gravity.TOP);
        LinearLayout left = column(); left.setGravity(Gravity.CENTER_HORIZONTAL);
        LinearLayout right = column(); right.setGravity(Gravity.CENTER_HORIZONTAL);
        body.addView(left, new LinearLayout.LayoutParams(0, -2, 0.82f)); body.addView(right, new LinearLayout.LayoutParams(0, -2, 1.18f));
        addDpad(left, 1f);
        LinearLayout primary = row(left); primary.setGravity(Gravity.CENTER);
        addIconControl(primary, R.drawable.action_back, "Back", 1f, this::back);
        addIconControl(primary, R.drawable.action_home, "Home", 1f, () -> action(c -> c.call("Input.Home", new JSONObject())));
        addVolume(primary, .58f);
        addNowPlaying(right, true);
        LinearLayout transport = row(right); transport.setGravity(Gravity.CENTER);
        addIconControl(transport, R.drawable.action_rewind, "Rewind", 1f, () -> seekStep("bigbackward"));
        addIconControl(transport, R.drawable.action_previous, "Previous", 1f, () -> goTo("previous"));
        addIconControl(transport, R.drawable.action_play_pause, "Play / Pause", 1.15f, this::playPause);
        addIconControl(transport, R.drawable.action_stop, "Stop", 1f, this::stop);
        addIconControl(transport, R.drawable.action_next, "Next", 1f, () -> goTo("next"));
        addIconControl(transport, R.drawable.action_fast_forward, "Fast forward", 1f, () -> seekStep("bigforward"));
        LinearLayout tail = row(right); tail.setGravity(Gravity.CENTER);
        ImageView settings = new ImageView(this); settings.setImageResource(R.drawable.action_settings); settings.setScaleType(ImageView.ScaleType.FIT_CENTER); settings.setContentDescription("Settings"); settings.setOnClickListener(v -> showSettings()); tail.addView(settings, new LinearLayout.LayoutParams(dp(66), dp(58)));
        addCategories(right);
        return outer;
    }

    private void addHeader(LinearLayout root) {
        LinearLayout header = row(root); header.setGravity(Gravity.CENTER_VERTICAL);
        TextView logo = text("Farfar", 23, TEXT, true); TextView accent = text("Remote", 23, CYAN, true);
        LinearLayout brand = new LinearLayout(this); brand.setGravity(Gravity.CENTER_VERTICAL); brand.addView(logo); brand.addView(accent);
        header.addView(brand, new LinearLayout.LayoutParams(0, -2, 1));
        LinearLayout connection = new LinearLayout(this); connection.setOrientation(LinearLayout.VERTICAL); connection.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        hostLabel = text(prefs.getString("host", "Kodi"), 12, TEXT, true); status = text("CONNECTING…", 11, MUTED, true);
        connection.addView(hostLabel); connection.addView(status); header.addView(connection);
        LinearLayout.LayoutParams power = new LinearLayout.LayoutParams(dp(58), dp(46)); power.leftMargin = dp(6);
        addPowerControl(header, power, 31);
    }

    private void addNowPlaying(LinearLayout root, boolean landscape) {
        LinearLayout card = column(); card.setPadding(dp(10), dp(8), dp(10), dp(8)); card.setBackground(panel());
        LinearLayout.LayoutParams cardLp = new LinearLayout.LayoutParams(-1, -2); cardLp.topMargin = dp(4); cardLp.bottomMargin = dp(5); root.addView(card, cardLp);
        LinearLayout upper = row(card); upper.setGravity(Gravity.CENTER_VERTICAL);
        poster = new ImageView(this); poster.setScaleType(ImageView.ScaleType.CENTER_CROP); poster.setBackground(round(Color.rgb(22, 39, 56), dp(9))); poster.setImageResource(R.drawable.placeholder_art);
        LinearLayout.LayoutParams posterLp = new LinearLayout.LayoutParams(landscape ? dp(82) : dp(62), landscape ? dp(88) : dp(68)); posterLp.rightMargin = dp(10); upper.addView(poster, posterLp);
        LinearLayout info = column(); upper.addView(info, new LinearLayout.LayoutParams(0, -2, 1));
        TextView eyebrow = text("NOW PLAYING", 10, CYAN, true); info.addView(eyebrow);
        titleText = text("Nothing playing", landscape ? 17 : 15, TEXT, true); titleText.setMaxLines(1); titleText.setEllipsize(android.text.TextUtils.TruncateAt.END); info.addView(titleText);
        episodeText = text("Kodi is ready when you are", 11, MUTED, false); episodeText.setMaxLines(1); episodeText.setEllipsize(android.text.TextUtils.TruncateAt.END); info.addView(episodeText);
        stateText = text("IDLE", 10, MUTED, true); info.addView(stateText);
        LinearLayout timeRow = row(card); timeRow.setGravity(Gravity.CENTER_VERTICAL);
        elapsedText = text("0:00", 10, MUTED, false); durationText = text("0:00", 10, MUTED, false);
        timeRow.addView(elapsedText);
        progress = new SeekBar(this); progress.setMax(1000); progress.setProgress(0);
        timeRow.addView(progress, new LinearLayout.LayoutParams(0, dp(32), 1)); timeRow.addView(durationText);
        progress.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int value, boolean fromUser) { if (fromUser) draggingSeek = true; }
            @Override public void onStartTrackingTouch(SeekBar seekBar) { draggingSeek = true; }
            @Override public void onStopTrackingTouch(SeekBar seekBar) { int value = seekBar.getProgress(); draggingSeek = false; seekPercent(value / 10.0); }
        });
        LinearLayout tracks = row(card); tracks.setGravity(Gravity.CENTER);
        addTrackButton(tracks, R.drawable.audio_selector, "Audio", true);
        addTrackButton(tracks, R.drawable.subtitle_selector, "Subtitles", false);
    }

    private void addTrackButton(LinearLayout row, int image, String label, boolean audio) {
        LinearLayout box = column(); box.setGravity(Gravity.CENTER); row.addView(box, new LinearLayout.LayoutParams(0, -2, 1));
        ImageView button = new ImageView(this); button.setImageResource(image); button.setScaleType(ImageView.ScaleType.FIT_CENTER); button.setContentDescription(label); button.setFocusable(true);
        box.addView(button, new LinearLayout.LayoutParams(-1, dp(54)));
        TextView current = text(audio ? "Audio: —" : "Subtitles: Off", 10, MUTED, false); current.setGravity(Gravity.CENTER); current.setMaxLines(1); current.setEllipsize(android.text.TextUtils.TruncateAt.END); box.addView(current);
        button.setOnClickListener(v -> showStreams(audio));
        if (audio) audioValue = current; else subsValue = current;
    }

    private void addDpad(LinearLayout parent, float weight) {
        FrameLayout pad = new FrameLayout(this); pad.setFocusable(true); pad.setContentDescription("D-pad: Up, Down, Left, Right, OK");
        ImageView image = new ImageView(this); image.setImageResource(R.drawable.dpad_ok); image.setScaleType(ImageView.ScaleType.FIT_CENTER); pad.addView(image, new FrameLayout.LayoutParams(-1, -1));
        pad.setOnTouchListener(new View.OnTouchListener() {
            @Override public boolean onTouch(View view, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    float x = (event.getX() / view.getWidth() - .5f) * 2f, y = (event.getY() / view.getHeight() - .5f) * 2f;
                    double radius = Math.sqrt(x*x + y*y);
                    if (radius < .34) { action(thisActivity -> thisActivity.call("Input.Select", new JSONObject())); }
                    else if (radius < 1.04) {
                        if (Math.abs(x) > Math.abs(y) * 1.08) action(c -> c.call(x < 0 ? "Input.Left" : "Input.Right", new JSONObject()));
                        else action(c -> c.call(y < 0 ? "Input.Up" : "Input.Down", new JSONObject()));
                    }
                    haptic();
                    return true;
                }
                return event.getAction() == MotionEvent.ACTION_DOWN || event.getAction() == MotionEvent.ACTION_MOVE;
            }
        });
        int size = isLandscape() ? dp(210) : dp(220);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(size, size);
        parent.addView(pad, lp);
    }

    private void addVolume(LinearLayout parent, float weight) {
        FrameLayout holder = new FrameLayout(this); holder.setContentDescription("Volume controls");
        ImageView art = new ImageView(this); art.setImageResource(R.drawable.volume_rocker); art.setScaleType(ImageView.ScaleType.FIT_CENTER); holder.addView(art, new FrameLayout.LayoutParams(-1, -1));
        // Weight the upper and lower halves through a transparent two-row overlay; the centre rule is inert.
        android.widget.LinearLayout zones = new android.widget.LinearLayout(this); zones.setOrientation(LinearLayout.VERTICAL);
        View top = new View(this); top.setContentDescription("Volume up"); View bottom = new View(this); bottom.setContentDescription("Volume down");
        top.setOnClickListener(v -> adjustVolume(10)); bottom.setOnClickListener(v -> adjustVolume(-10));
        TextView mute = text("MUTE", 8, MUTED, true); mute.setGravity(Gravity.CENTER); mute.setContentDescription("Mute"); mute.setOnClickListener(v -> toggleMute());
        zones.addView(top, new LinearLayout.LayoutParams(-1, 0, 5)); zones.addView(mute, new LinearLayout.LayoutParams(-1, 0, 1)); zones.addView(bottom, new LinearLayout.LayoutParams(-1, 0, 5));
        holder.addView(zones, new FrameLayout.LayoutParams(-1, -1));
        holder.setMinimumHeight(isLandscape() ? dp(116) : dp(190));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, isLandscape() ? dp(145) : dp(212), isLandscape() ? .95f : weight); lp.leftMargin = dp(6); lp.rightMargin = dp(6); parent.addView(holder, lp);
    }

    private void addIconControl(LinearLayout parent, int res, String label, float weight, Runnable action) {
        LinearLayout box = column(); box.setGravity(Gravity.CENTER); box.setFocusable(true); box.setContentDescription(label); box.setOnClickListener(v -> { haptic(); action.run(); });
        ImageView image = (res == R.drawable.action_home || res == R.drawable.action_stop)
                ? new EdgeClippedImageView(this, res == R.drawable.action_stop) : new ImageView(this);
        image.setImageResource(res); image.setScaleType(ImageView.ScaleType.FIT_CENTER); box.addView(image, new LinearLayout.LayoutParams(-1, dp(isLandscape() ? 54 : 48)));
        TextView caption = text(label, isLandscape() ? 9 : 9, MUTED, false); caption.setGravity(Gravity.CENTER); caption.setMaxLines(1); box.addView(caption);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -2, weight); lp.leftMargin = dp(1); lp.rightMargin = dp(1); parent.addView(box, lp);
        box.setOnLongClickListener(v -> false);
    }

    private void addPowerControl(LinearLayout parent, LinearLayout.LayoutParams layout, int iconHeightDp) {
        LinearLayout box = column(); box.setGravity(Gravity.CENTER); box.setFocusable(true);
        box.setContentDescription("Power off Kodi device");
        box.setOnClickListener(v -> { haptic(); confirmKodiShutdown(); });
        box.addView(new PowerIconView(this), new LinearLayout.LayoutParams(-1, dp(iconHeightDp)));
        TextView caption = text("Power Off", 9, MUTED, false); caption.setGravity(Gravity.CENTER); caption.setMaxLines(1); box.addView(caption);
        parent.addView(box, layout);
    }

    /** Canvas-drawn API 19-compatible power glyph; no bitmap or support-library dependency. */
    private final class PowerIconView extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        PowerIconView(Context context) { super(context); setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO); }
        @Override protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            float size = Math.min(getWidth(), getHeight()) * 0.62f;
            float cx = getWidth() / 2f, cy = getHeight() / 2f, radius = size * 0.42f;
            paint.setColor(RED); paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(Math.max(dp(2), size * 0.09f)); paint.setStrokeCap(Paint.Cap.ROUND);
            android.graphics.RectF ring = new android.graphics.RectF(cx - radius, cy - radius, cx + radius, cy + radius);
            canvas.drawArc(ring, 315f, 270f, false, paint);
            canvas.drawLine(cx, cy - size * 0.50f, cx, cy + size * 0.03f, paint);
        }
    }

    private void addTransport(LinearLayout root) {
        LinearLayout r = row(root); r.setGravity(Gravity.CENTER);
        addIconControl(r, R.drawable.action_rewind, "Rewind", 1f, () -> seekStep("bigbackward"));
        addIconControl(r, R.drawable.action_previous, "Previous", 1f, () -> goTo("previous"));
        addIconControl(r, R.drawable.action_next, "Next", 1f, () -> goTo("next"));
        addIconControl(r, R.drawable.action_fast_forward, "Forward", 1f, () -> seekStep("bigforward"));
    }

    private void addCategories(LinearLayout parent) {
        LinearLayout categories = row(parent); categories.setGravity(Gravity.CENTER);
        addImageOnlyControl(categories, R.drawable.category_movies, "Movies", () -> activate("videos", new String[]{"MovieTitles"}));
        addImageOnlyControl(categories, R.drawable.category_tv_shows, "TV Shows", () -> activate("videos", new String[]{"TVShowTitles"}));
        addImageOnlyControl(categories, R.drawable.category_music, "Music", () -> activate("music", null));
        addImageOnlyControl(categories, R.drawable.category_addons, "Add-ons", () -> activate("addons", null));
        LinearLayout favoriteRow = row(parent); favoriteRow.setGravity(Gravity.CENTER);
        TextView favorites = text("☆  Favorites", 12, CYAN, true); favorites.setGravity(Gravity.CENTER); favorites.setPadding(dp(16), 0, dp(16), 0);
        favorites.setBackground(round(PANEL, dp(16))); favorites.setContentDescription("Open saved Kodi folder favorites"); favorites.setFocusable(true);
        favorites.setOnClickListener(v -> showFavorites());
        LinearLayout.LayoutParams favoriteLp = new LinearLayout.LayoutParams(-2, dp(36)); favoriteLp.topMargin = dp(1); favoriteRow.addView(favorites, favoriteLp);
    }

    /** Clips adjacent sprite-sheet fragments from only the two affected action PNGs. */
    private final class EdgeClippedImageView extends ImageView {
        private final boolean trimLeft;
        EdgeClippedImageView(Context context, boolean trimLeft) { super(context); this.trimLeft = trimLeft; }
        @Override protected void onDraw(Canvas canvas) {
            Drawable drawable = getDrawable();
            if (drawable == null || drawable.getIntrinsicWidth() <= 0 || drawable.getIntrinsicHeight() <= 0) { super.onDraw(canvas); return; }
            RectF imageBounds = new RectF(0, 0, drawable.getIntrinsicWidth(), drawable.getIntrinsicHeight());
            getImageMatrix().mapRect(imageBounds);
            float trim = imageBounds.width() * 0.08f;
            int save = canvas.save();
            canvas.clipRect(trimLeft ? imageBounds.left + trim : imageBounds.left,
                    imageBounds.top,
                    trimLeft ? imageBounds.right : imageBounds.right - trim,
                    imageBounds.bottom);
            super.onDraw(canvas);
            canvas.restoreToCount(save);
        }
    }

    private static final String FAVORITES_PREF = "folder_favorites_v1";

    private void showFavorites() {
        final AlertDialog dialog = new AlertDialog.Builder(this).setTitle("Kodi folder favorites").create();
        LinearLayout content = column(); content.setPadding(dp(16), dp(8), dp(16), dp(8));
        TextView hint = text("Save the folder currently open in Kodi, then tap it here to return.", 12, MUTED, false);
        hint.setPadding(0, 0, 0, dp(8)); content.addView(hint);
        ScrollView listScroll = new ScrollView(this); listScroll.setFillViewport(false); listScroll.setVerticalScrollBarEnabled(false);
        LinearLayout list = column(); listScroll.addView(list); content.addView(listScroll, new LinearLayout.LayoutParams(-1, dp(190)));
        JSONArray saved = readFolderFavorites();
        if (saved.length() == 0) {
            TextView empty = text("No saved folders yet.", 13, MUTED, false); empty.setGravity(Gravity.CENTER); list.addView(empty, new LinearLayout.LayoutParams(-1, dp(64)));
        } else {
            for (int i = 0; i < saved.length(); i++) {
                JSONObject favorite = saved.optJSONObject(i); if (favorite == null) continue;
                final String name = favorite.optString("name", "Kodi folder");
                final String path = favorite.optString("path", "");
                final String window = favorite.optString("window", "videos");
                if (path.isEmpty()) continue;
                LinearLayout entry = row(list); entry.setGravity(Gravity.CENTER_VERTICAL); entry.setPadding(dp(8), 0, dp(4), 0); entry.setBackground(round(PANEL, dp(9)));
                LinearLayout.LayoutParams entryLp = new LinearLayout.LayoutParams(-1, dp(48)); entryLp.bottomMargin = dp(5); entry.setLayoutParams(entryLp);
                LinearLayout label = column(); label.setGravity(Gravity.CENTER_VERTICAL); label.setContentDescription("Open favorite " + name); label.setFocusable(true);
                label.addView(text(name, 13, TEXT, true)); TextView pathText = text(path, 9, MUTED, false); pathText.setSingleLine(true); pathText.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE); label.addView(pathText);
                entry.addView(label, new LinearLayout.LayoutParams(0, -1, 1)); label.setOnClickListener(v -> { dialog.dismiss(); openFolderFavorite(window, path); });
                TextView remove = text("×", 22, MUTED, true); remove.setGravity(Gravity.CENTER); remove.setContentDescription("Remove favorite " + name); entry.addView(remove, new LinearLayout.LayoutParams(dp(38), -1));
                remove.setOnClickListener(v -> new AlertDialog.Builder(this).setMessage("Remove “" + name + "” from favorites?")
                        .setNegativeButton("Cancel", null).setPositiveButton("Remove", (d, which) -> { removeFolderFavorite(path); dialog.dismiss(); showFavorites(); }).show());
            }
        }
        dialog.setView(content);
        dialog.setButton(AlertDialog.BUTTON_POSITIVE, "Save current folder", (android.content.DialogInterface.OnClickListener) null);
        dialog.setButton(AlertDialog.BUTTON_NEGATIVE, "Close", (android.content.DialogInterface.OnClickListener) null);
        dialog.setOnShowListener(d -> {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> { dialog.dismiss(); saveCurrentFolder(); });
        });
        dialog.show();
    }

    private JSONArray readFolderFavorites() {
        try { return new JSONArray(prefs.getString(FAVORITES_PREF, "[]")); }
        catch (Exception ignored) { return new JSONArray(); }
    }

    private void saveCurrentFolder() {
        toast("Reading the current Kodi folder…");
        userRequestExecutor().execute(() -> {
            String path = null, name = null, window = "videos", error = null;
            try {
                JSONObject labels = client().call("XBMC.GetInfoLabels", new JSONObject().put("labels",
                        new JSONArray().put("Container.FolderPath").put("Container.FolderName").put("Container.Content")));
                path = labels.optString("Container.FolderPath", "").trim();
                name = labels.optString("Container.FolderName", "").trim();
                String content = labels.optString("Container.Content", "").toLowerCase(Locale.US);
                if (content.contains("song") || content.contains("album") || content.contains("artist") || content.contains("music")) window = "music";
                if (path.isEmpty()) error = "Kodi did not report an open folder. Open a folder in Kodi first.";
                else if (path.equalsIgnoreCase("root") || path.equalsIgnoreCase("sources://")) error = "Open a folder below the Kodi root before saving a favorite.";
            } catch (Exception e) { error = e.getMessage() == null ? "Could not read the current Kodi folder." : e.getMessage(); }
            final String currentPath = path, currentName = name, currentWindow = window, failure = error;
            handler.post(() -> {
                if (isFinishing() || destroyed) return;
                if (failure != null) { toast(failure); return; }
                promptFavoriteName(currentPath, currentName, currentWindow);
            });
        });
    }

    private void promptFavoriteName(String path, String suggestedName, String window) {
        EditText nameField = edit(suggestedName == null || suggestedName.isEmpty() ? pathLeaf(path) : suggestedName,
                "Favorite name", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        new AlertDialog.Builder(this).setTitle("Save Kodi folder").setView(nameField)
                .setNegativeButton("Cancel", null).setPositiveButton("Save", (dialog, which) -> {
                    String name = nameField.getText().toString().trim();
                    if (name.isEmpty()) name = pathLeaf(path);
                    if (saveFolderFavorite(name, path, window)) { toast("Folder favorite saved."); showFavorites(); }
                }).show();
    }

    private String pathLeaf(String path) {
        if (path == null || path.isEmpty()) return "Kodi folder";
        String clean = path.endsWith("/") && path.length() > 1 ? path.substring(0, path.length() - 1) : path;
        int slash = Math.max(clean.lastIndexOf('/'), clean.lastIndexOf('\\'));
        String leaf = clean.substring(slash + 1);
        return leaf.isEmpty() ? "Kodi folder" : leaf;
    }

    private boolean saveFolderFavorite(String name, String path, String window) {
        JSONArray old = readFolderFavorites(), updated = new JSONArray();
        try {
            for (int i = 0; i < old.length(); i++) {
                JSONObject item = old.optJSONObject(i);
                if (item != null && !path.equals(item.optString("path", ""))) updated.put(item);
            }
            updated.put(new JSONObject().put("name", name).put("path", path).put("window", window));
            prefs.edit().putString(FAVORITES_PREF, updated.toString()).apply();
            return true;
        } catch (Exception e) { toast("Could not save this folder favorite."); return false; }
    }

    private void removeFolderFavorite(String path) {
        JSONArray old = readFolderFavorites(), updated = new JSONArray();
        for (int i = 0; i < old.length(); i++) {
            JSONObject item = old.optJSONObject(i);
            if (item != null && !path.equals(item.optString("path", ""))) updated.put(item);
        }
        prefs.edit().putString(FAVORITES_PREF, updated.toString()).apply();
    }

    private void openFolderFavorite(String window, String path) {
        action(c -> c.call("GUI.ActivateWindow", new JSONObject().put("window", window).put("parameters", new JSONArray().put(path))));
    }

    private void addImageOnlyControl(LinearLayout parent, int res, String label, Runnable action) {
        ImageView image = new ImageView(this); image.setImageResource(res); image.setScaleType(ImageView.ScaleType.FIT_CENTER); image.setContentDescription(label); image.setFocusable(true); image.setOnClickListener(v -> { haptic(); action.run(); });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(isLandscape() ? 67 : 72), 1f); lp.setMargins(dp(1), 0, dp(1), 0); parent.addView(image, lp);
    }

    private void showSettings() {
        inSettings = true;
        updateSettingsBackCallback();
        if (!settingsImeModeSet) { previousSoftInputMode = getWindow().getAttributes().softInputMode; settingsImeModeSet = true; }
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        ScrollView scroll = new ScrollView(this); settingsScroll = scroll; scroll.setFillViewport(true); scroll.setVerticalScrollBarEnabled(false);
        scroll.setClipToPadding(false); scroll.setBackgroundResource(isLandscape() ? R.drawable.settings_bg_landscape : R.drawable.settings_bg_portrait);
        LinearLayout root = column(); root.setPadding(dp(12), dp(10), dp(12), dp(20)); scroll.addView(root);

        LinearLayout header = row(root); header.setGravity(Gravity.CENTER_VERTICAL); header.setPadding(dp(10), 0, dp(8), 0); header.setBackgroundResource(R.drawable.settings_header);
        ImageView headerIcon = settingsIcon(R.drawable.settings_ic_settings, "Settings"); header.addView(headerIcon, new LinearLayout.LayoutParams(dp(34), dp(34)));
        LinearLayout headerText = column(); headerText.setPadding(dp(8), 0, 0, 0); header.addView(headerText, new LinearLayout.LayoutParams(0, -2, 1));
        headerText.addView(text("Settings", 21, TEXT, true)); headerText.addView(text(getResources().getBoolean(R.bool.dedicated_os) ? "FarfarRemote OS" : "Kodi Remote App", 11, MUTED, false));
        TextView close = text("×", 30, CYAN, true); close.setGravity(Gravity.CENTER); close.setContentDescription("Close settings"); close.setOnClickListener(v -> closeSettings()); header.addView(close, new LinearLayout.LayoutParams(dp(42), dp(46)));

        LinearLayout connection = settingsCard(root, "Kodi Connection", R.drawable.settings_ic_wifi);
        addFieldLabel(connection, "Host / IP Address");
        EditText host = edit(prefs.getString("host", ""), "Hostname or IP address", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        connection.addView(host, fullField());
        LinearLayout account = row(connection);
        LinearLayout portBox = column(); account.addView(portBox, new LinearLayout.LayoutParams(dp(92), -2)); addFieldLabel(portBox, "Port");
        EditText port = edit(prefs.getString("port", "8080"), "8080", InputType.TYPE_CLASS_NUMBER); portBox.addView(port, fullField());
        LinearLayout userBox = column(); LinearLayout.LayoutParams userBoxLp = new LinearLayout.LayoutParams(0, -2, 1); userBoxLp.leftMargin = dp(8); account.addView(userBox, userBoxLp); addFieldLabel(userBox, "Username");
        EditText username = edit(prefs.getString("user", ""), "Kodi username", InputType.TYPE_CLASS_TEXT); userBox.addView(username, fullField());
        addFieldLabel(connection, "Password");
        EditText password = edit(prefs.getString("pass", ""), "Kodi password", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD); connection.addView(password, fullField());
        Switch showPassword = settingsSwitch(connection, "Show password", false, null, null);
        LinearLayout passwordLine = (LinearLayout) showPassword.getParent();
        LinearLayout passwordLabels = (LinearLayout) passwordLine.getChildAt(0);
        TextView passwordLabel = (TextView) passwordLabels.getChildAt(0);
        showPassword.setOnCheckedChangeListener((button, checked) -> {
            passwordLabel.setText(checked ? "Hide password" : "Show password");
            int pos = password.getSelectionStart(); password.setInputType(checked ? InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD : InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD); password.setSelection(Math.max(0, pos));
        });
        LinearLayout actions = row(connection);
        actionButton(actions, R.drawable.settings_ic_test, "Test Connection", false, () -> testConnection(host, port, username, password));
        actionButton(actions, R.drawable.settings_ic_save, "Save", true, () -> saveConnection(host, port, username, password));
        LinearLayout discoverRow = row(connection); discoverRow.setGravity(Gravity.CENTER);
        discoverRow.addView(makeActionButton(R.drawable.settings_ic_wifi, "Find My Kodi", false, () -> findKodi(host, port, username, password)), new LinearLayout.LayoutParams(-1, dp(46)));
        LinearLayout wifiRow = row(connection); wifiRow.setGravity(Gravity.CENTER);
        wifiRow.addView(makeActionButton(R.drawable.settings_ic_wifi, "Wi-Fi Settings", false, this::openWifiSettings), new LinearLayout.LayoutParams(dp(220), dp(48)));
        settingsFeedback = text(connected ? "Kodi connected" : "Kodi offline · settings are available", 12, connected ? GREEN : MUTED, false);
        settingsFeedback.setPadding(dp(4), dp(6), dp(4), dp(2)); connection.addView(settingsFeedback);

        LinearLayout display = settingsCard(root, "Display", R.drawable.settings_ic_display);
        LinearLayout orientation = new LinearLayout(this); orientation.setOrientation(LinearLayout.HORIZONTAL); orientation.setGravity(Gravity.CENTER);
        addOrientation(orientation, "Portrait", "portrait", R.drawable.settings_ic_portrait);
        addOrientation(orientation, "Landscape", "landscape", R.drawable.settings_ic_landscape);
        addOrientation(orientation, "Auto", "auto", R.drawable.settings_ic_auto);
        display.addView(orientation, new LinearLayout.LayoutParams(-1, dp(70)));
        selectOrientation(orientation, prefs.getString("orientation", "portrait"));
        for (int i = 0; i < orientation.getChildCount(); i++) {
            RadioButton option = (RadioButton) orientation.getChildAt(i);
            option.setOnCheckedChangeListener((button, checked) -> {
                if (!checked) return;
                for (int n = 0; n < orientation.getChildCount(); n++) { RadioButton other = (RadioButton) orientation.getChildAt(n); if (other != button) other.setChecked(false); }
                prefs.edit().putString("orientation", String.valueOf(button.getTag())).apply(); applyOrientationPreference();
            });
        }
        settingsSwitch(display, "Keep Screen Awake", prefs.getBoolean("keep_awake", false), "Override Android's configured screen timeout", (button, checked) -> { prefs.edit().putBoolean("keep_awake", checked).apply(); applyKeepAwake(); });
        if (isDedicatedOs()) addBatteryModeSettings(root);

        LinearLayout remote = settingsCard(root, "Remote", R.drawable.settings_ic_remote);
        settingsSwitch(remote, "Auto Reconnect", prefs.getBoolean("auto_reconnect", true), "Reconnect to Kodi when it becomes available", (button, checked) -> prefs.edit().putBoolean("auto_reconnect", checked).apply());
        boolean hapticSupported = hasVibrator();
        settingsSwitch(remote, "Haptic Feedback", prefs.getBoolean("haptics", false), hapticSupported ? "Vibration on supported controls" : "Not supported on this device", (button, checked) -> prefs.edit().putBoolean("haptics", checked).apply()).setEnabled(hapticSupported);

        LinearLayout system = settingsCard(root, "System Information", R.drawable.settings_ic_info);
        String model = android.os.Build.MODEL, androidVersion = android.os.Build.VERSION.RELEASE + " (API " + android.os.Build.VERSION.SDK_INT + ")";
        String appVersion = "Unknown"; try { PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0); appVersion = info.versionName; } catch (Exception ignored) { }
        system.addView(infoRow("FarfarRemote", appVersion)); system.addView(infoRow("Android", androidVersion)); system.addView(infoRow("Device", model));
        LinearLayout kodiInfo = infoRow("Kodi", connected ? "Connected" : "Offline"); settingsKodiStatus = (TextView) kodiInfo.getChildAt(1); settingsKodiStatus.setTextColor(connected ? GREEN : RED); system.addView(kodiInfo);

        LinearLayout coffee = new LinearLayout(this); coffee.setGravity(Gravity.CENTER); coffee.setPadding(0, dp(8), 0, dp(6)); root.addView(coffee, new LinearLayout.LayoutParams(-1, -2));
        LinearLayout coffeeButton = new LinearLayout(this); coffeeButton.setGravity(Gravity.CENTER); coffeeButton.setOrientation(LinearLayout.HORIZONTAL); coffeeButton.setPadding(dp(13), 0, dp(13), 0); coffeeButton.setBackgroundResource(R.drawable.settings_button_coffee); coffeeButton.setContentDescription("Buy Me a Coffee — opens external website");
        coffeeButton.addView(settingsIcon(R.drawable.settings_ic_coffee, ""), new LinearLayout.LayoutParams(dp(22), dp(22)));
        TextView coffeeText = text("Buy Me a Coffee", 13, Color.rgb(246, 215, 174), true); coffeeText.setGravity(Gravity.CENTER); LinearLayout.LayoutParams coffeeTextLp = new LinearLayout.LayoutParams(0, -1, 1); coffeeTextLp.leftMargin = dp(7); coffeeButton.addView(coffeeText, coffeeTextLp);
        coffeeButton.addView(settingsIcon(R.drawable.settings_ic_arrow, "Opens website"), new LinearLayout.LayoutParams(dp(18), dp(18)));
        coffeeButton.setOnClickListener(v -> openCoffeeLink()); coffee.addView(coffeeButton, new LinearLayout.LayoutParams(dp(260), dp(50)));
        screen.removeAllViews(); screen.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
    }

    private void addBatteryModeSettings(LinearLayout root) {
        LinearLayout battery = settingsCard(root, "Battery Mode", R.drawable.settings_ic_display);
        TextView profileHint = text("Reduce background Kodi checks while keeping direct controls responsive.", 10, MUTED, false);
        profileHint.setPadding(dp(5), dp(2), dp(5), dp(5)); battery.addView(profileHint);
        RadioGroup modes = batteryChoices(battery, new String[]{"Normal", "Balanced", "Max Saving"},
                new String[]{"normal", "balanced", "maximum"}, "os_battery_mode", "normal");
        modes.setContentDescription("Battery mode profile");
        TextView modeHint = text("Normal: current refresh rate. Balanced: playback every 5 seconds. Maximum: playback every 10 seconds. Recent input always refreshes promptly.", 10, MUTED, false);
        modeHint.setPadding(dp(5), dp(4), dp(5), dp(5)); battery.addView(modeHint);
        battery.addView(text("Kodi idle refresh (Balanced / Maximum)", 11, TEXT, true));
        RadioGroup idle = batteryChoices(battery, new String[]{"2 sec", "5 sec", "10 sec"},
                new String[]{"2", "5", "10"}, "os_battery_idle_seconds", "5");
        idle.setContentDescription("Kodi idle refresh interval");
        settingsSwitch(battery, "Reduced Brightness", prefs.getBoolean("os_battery_dim", false),
                "Use 25% window brightness while FarfarRemote OS is visible", (button, checked) -> {
                    prefs.edit().putBoolean("os_battery_dim", checked).apply(); applyReducedBrightness();
                });
        TextView screenHint = text("Screen off suspends Kodi polling. Android's normal screen timeout is used unless Keep Screen Awake is enabled above.", 10, MUTED, false);
        screenHint.setPadding(dp(5), dp(2), dp(5), dp(2)); battery.addView(screenHint);
    }

    private RadioGroup batteryChoices(LinearLayout parent, String[] labels, String[] values, String key, String fallback) {
        RadioGroup group = new RadioGroup(this); group.setOrientation(LinearLayout.HORIZONTAL);
        String selected = prefs.getString(key, fallback);
        for (int i = 0; i < labels.length; i++) {
            RadioButton option = new RadioButton(this); option.setId(View.generateViewId()); option.setText(labels[i]);
            option.setTextColor(TEXT); option.setTextSize(10); option.setTag(values[i]); option.setGravity(Gravity.CENTER);
            option.setButtonDrawable(android.R.color.transparent); option.setBackgroundResource(R.drawable.settings_orientation_background);
            option.setPadding(dp(2), dp(2), dp(2), dp(2));
            RadioGroup.LayoutParams lp = new RadioGroup.LayoutParams(0, dp(42), 1f);
            lp.setMargins(dp(2), dp(4), dp(2), dp(4)); group.addView(option, lp);
            if (values[i].equals(selected)) group.check(option.getId());
        }
        group.setOnCheckedChangeListener((parentGroup, checkedId) -> {
            RadioButton choice = parentGroup.findViewById(checkedId);
            if (choice == null) return;
            prefs.edit().putString(key, String.valueOf(choice.getTag())).apply();
            if (activityStarted) schedulePoll(0);
        });
        parent.addView(group, new LinearLayout.LayoutParams(-1, dp(50)));
        return group;
    }

    private LinearLayout settingsCard(LinearLayout root, String title, int icon) {
        LinearLayout card = column(); card.setBackground(panel()); card.setPadding(dp(10), dp(8), dp(10), dp(9));
        LinearLayout.LayoutParams cardLp = new LinearLayout.LayoutParams(-1, -2); cardLp.topMargin = dp(7); cardLp.bottomMargin = dp(4); root.addView(card, cardLp);
        LinearLayout heading = row(card); heading.setBackgroundResource(R.drawable.settings_section); heading.setPadding(dp(9), 0, dp(8), 0);
        heading.addView(settingsIcon(icon, title), new LinearLayout.LayoutParams(dp(26), dp(26)));
        TextView label = text(title, 15, TEXT, true); LinearLayout.LayoutParams labelLp = new LinearLayout.LayoutParams(-1, dp(48)); labelLp.leftMargin = dp(8); heading.addView(label, labelLp);
        return card;
    }

    private ImageView settingsIcon(int resource, String description) {
        ImageView icon = new ImageView(this); icon.setImageResource(resource); icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
        if (description != null && !description.isEmpty()) icon.setContentDescription(description); return icon;
    }

    private void addFieldLabel(LinearLayout parent, String value) {
        TextView label = text(value, 12, MUTED, true); LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2); lp.topMargin = dp(7); lp.leftMargin = dp(3); parent.addView(label, lp);
    }

    private LinearLayout infoRow(String label, String value) {
        LinearLayout line = new LinearLayout(this); line.setOrientation(LinearLayout.HORIZONTAL); line.setGravity(Gravity.CENTER_VERTICAL);
        line.setLayoutParams(new LinearLayout.LayoutParams(-1, -2));
        TextView key = text(label, 12, MUTED, false); line.addView(key, new LinearLayout.LayoutParams(0, dp(34), .42f));
        TextView val = text(value, 13, TEXT, true); line.addView(val, new LinearLayout.LayoutParams(0, dp(34), .58f));
        line.setPadding(dp(5), 0, dp(5), 0); return line;
    }

    private Switch settingsSwitch(LinearLayout parent, String title, boolean checked, String summary, CompoundButton.OnCheckedChangeListener listener) {
        LinearLayout line = row(parent); line.setPadding(dp(5), dp(4), dp(3), dp(4));
        LinearLayout labels = column(); line.addView(labels, new LinearLayout.LayoutParams(0, -2, 1));
        labels.addView(text(title, 13, TEXT, true)); if (summary != null) { TextView detail = text(summary, 10, MUTED, false); labels.addView(detail); }
        Switch toggle = new Switch(this); toggle.setTextOn(""); toggle.setTextOff(""); toggle.setChecked(checked); toggle.setSwitchMinWidth(dp(64)); toggle.setThumbDrawable(toggleThumbs()); toggle.setTrackDrawable(getResources().getDrawable(R.drawable.settings_toggle_track));
        line.addView(toggle, new LinearLayout.LayoutParams(dp(72), dp(46)));
        if (listener != null) toggle.setOnCheckedChangeListener(listener);
        return toggle;
    }

    private StateListDrawable toggleThumbs() {
        StateListDrawable states = new StateListDrawable();
        states.addState(new int[]{android.R.attr.state_checked}, getResources().getDrawable(R.drawable.settings_toggle_on));
        states.addState(new int[]{}, getResources().getDrawable(R.drawable.settings_toggle_off)); return states;
    }

    private boolean hasVibrator() { try { android.os.Vibrator vibrator = (android.os.Vibrator) getSystemService(Context.VIBRATOR_SERVICE); return vibrator != null && vibrator.hasVibrator(); } catch (Exception ignored) { return false; } }

    private void addOrientation(LinearLayout group, String label, String tag, int iconResource) {
        RadioButton rb = new RadioButton(this); rb.setId(View.generateViewId()); rb.setText(label); rb.setTextColor(TEXT); rb.setTextSize(11); rb.setTag(tag); rb.setGravity(Gravity.CENTER); rb.setButtonDrawable(android.R.color.transparent); rb.setBackgroundResource(R.drawable.settings_orientation_background); rb.setPadding(dp(2), dp(4), dp(2), dp(4)); rb.setCompoundDrawablePadding(dp(2));
        Drawable icon = getResources().getDrawable(iconResource); icon.setBounds(0, 0, dp(22), dp(22)); rb.setCompoundDrawables(null, icon, null, null);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(64), 1); lp.setMargins(dp(3), dp(3), dp(3), dp(3)); group.addView(rb, lp);
    }
    private void selectOrientation(LinearLayout group, String value) { for (int i = 0; i < group.getChildCount(); i++) { RadioButton rb = (RadioButton) group.getChildAt(i); rb.setChecked(value.equals(rb.getTag())); } }

    private void closeSettings() { stopKodiDiscovery(true); buildScreen(); if (isDedicatedOs()) schedulePoll(0); }

    private void updateSettingsBackCallback() {
        if (android.os.Build.VERSION.SDK_INT < 33 || getResources().getBoolean(R.bool.dedicated_os)) return;
        if (inSettings && settingsBackCallback == null) {
            settingsBackCallback = Api33BackHandler.register(this, this::closeSettings);
        } else if (!inSettings && settingsBackCallback != null) {
            Api33BackHandler.unregister(this, settingsBackCallback);
            settingsBackCallback = null;
        }
    }

    private void openCoffeeLink() {
        Uri uri = Uri.parse(COFFEE_URL);
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); }
        catch (ActivityNotFoundException e) {
            try {
                ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null) throw new IllegalStateException("Clipboard is unavailable");
                clipboard.setPrimaryClip(ClipData.newPlainText("Buy Me a Coffee", COFFEE_URL));
                toast("No browser is installed. The support URL was copied to the clipboard.");
            } catch (Exception clipboardError) {
                new AlertDialog.Builder(this).setMessage("No browser is available. You can copy this address later:\n" + COFFEE_URL).setPositiveButton("Close", null).show();
            }
        }
    }

    private void testConnection(EditText host, EditText port, EditText username, EditText password) {
        try {
            KodiClient client = new KodiClient(host.getText().toString(), port.getText().toString(), username.getText().toString(), password.getText().toString());
            settingsMessage("Testing connection…", MUTED);
            userRequestExecutor().execute(() -> { String message; boolean ok;
                try { client.ping(); JSONObject app = client.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("name"))); String n = app.optString("name", "Kodi"); message = "Connected · " + n; ok = true; }
                catch (Exception e) { message = e.getMessage() == null ? "Kodi anslöt inte." : e.getMessage(); ok = false; }
                final String msg = message; final boolean success = ok; handler.post(() -> { connected = success; settingsMessage(msg, success ? GREEN : RED); updateHeader(); });
            });
        } catch (Exception e) { settingsMessage(e.getMessage(), RED); }
    }

    private void findKodi(EditText hostField, EditText portField, EditText usernameField, EditText passwordField) {
        stopKodiDiscovery(true);
        discoveryHostField = hostField; discoveryPortField = portField; discoveryUsernameField = usernameField; discoveryPasswordField = passwordField;
        nsdManager = (NsdManager) getSystemService(Context.NSD_SERVICE);
        if (nsdManager == null) { settingsMessage("Network service discovery is unavailable on this Android device.", RED); return; }
        pendingKodiServices.clear(); resolvedKodiEndpoints.clear(); seenKodiEndpoints.clear(); resolvingKodiService = false; kodiDiscoveryTimedOut = false;
        discoveryDialog = new AlertDialog.Builder(this).setTitle("Find My Kodi")
                .setMessage("Searching the local network for Kodi HTTP JSON-RPC…")
                .setNegativeButton("Cancel", (dialog, which) -> stopKodiDiscovery(true)).create();
        discoveryDialog.setOnCancelListener(dialog -> stopKodiDiscovery(true));
        discoveryDialog.show();
        kodiDiscovery = new NsdManager.DiscoveryListener() {
            @Override public void onDiscoveryStarted(String serviceType) { }
            @Override public void onServiceFound(NsdServiceInfo service) {
                if (!KODI_HTTP_SERVICE.equals(service.getServiceType())) return;
                pendingKodiServices.add(service); resolveNextKodiService();
            }
            @Override public void onServiceLost(NsdServiceInfo service) { }
            @Override public void onDiscoveryStopped(String serviceType) { }
            @Override public void onStartDiscoveryFailed(String serviceType, int errorCode) {
                stopKodiDiscovery(true); showKodiDiscoveryError("Android could not start local network discovery (" + errorCode + ").");
            }
            @Override public void onStopDiscoveryFailed(String serviceType, int errorCode) { stopKodiDiscovery(false); }
        };
        try {
            nsdManager.discoverServices(KODI_HTTP_SERVICE, NsdManager.PROTOCOL_DNS_SD, kodiDiscovery);
            kodiDiscoveryTimeout = () -> {
                kodiDiscoveryTimeout = null;
                kodiDiscoveryTimedOut = true;
                stopDiscoveryOnly();
                resolveNextKodiService();
                if (discoveryDialog == null) return;
                kodiDiscoveryTimeout = () -> {
                    kodiDiscoveryTimeout = null;
                    pendingKodiServices.clear();
                    resolvingKodiService = false;
                    showKodiCandidates();
                };
                handler.postDelayed(kodiDiscoveryTimeout, 2000);
            };
            handler.postDelayed(kodiDiscoveryTimeout, KODI_DISCOVERY_TIMEOUT_MS);
        } catch (Exception e) {
            stopKodiDiscovery(true); showKodiDiscoveryError("Could not search for Kodi: " + safeMessage(e));
        }
    }

    private void resolveNextKodiService() {
        if (resolvingKodiService || pendingKodiServices.isEmpty()) {
            if (!resolvingKodiService && pendingKodiServices.isEmpty() && kodiDiscoveryTimedOut) showKodiCandidates();
            return;
        }
        resolvingKodiService = true;
        NsdServiceInfo service = pendingKodiServices.removeFirst();
        try {
            nsdManager.resolveService(service, new NsdManager.ResolveListener() {
                @Override public void onResolveFailed(NsdServiceInfo ignored, int errorCode) {
                    resolvingKodiService = false; resolveNextKodiService();
                }
                @Override public void onServiceResolved(NsdServiceInfo found) {
                    java.net.InetAddress address = found.getHost();
                    if (address != null && found.getPort() > 0) {
                        KodiEndpoint endpoint = new KodiEndpoint(found.getServiceName(), address.getHostAddress(), found.getPort());
                        if (seenKodiEndpoints.add(endpoint.key())) resolvedKodiEndpoints.add(endpoint);
                    }
                    resolvingKodiService = false; resolveNextKodiService();
                }
            });
        } catch (Exception e) { resolvingKodiService = false; resolveNextKodiService(); }
    }

    private void stopDiscoveryOnly() {
        if (kodiDiscoveryTimeout != null) { handler.removeCallbacks(kodiDiscoveryTimeout); kodiDiscoveryTimeout = null; }
        if (nsdManager != null && kodiDiscovery != null) {
            try { nsdManager.stopServiceDiscovery(kodiDiscovery); } catch (Exception ignored) { }
            kodiDiscovery = null;
        }
    }

    private void stopKodiDiscovery(boolean dismiss) {
        kodiDiscoveryTimedOut = false;
        pendingKodiServices.clear();
        stopDiscoveryOnly();
        if (dismiss && discoveryDialog != null) { AlertDialog dialog = discoveryDialog; discoveryDialog = null; if (dialog.isShowing()) dialog.dismiss(); }
        else discoveryDialog = null;
    }

    private void showKodiDiscoveryError(String message) {
        if (destroyed || !inSettings) return;
        settingsMessage(message, RED);
    }

    private void showKodiCandidates() {
        if (destroyed || !inSettings || discoveryDialog == null) return;
        if (kodiDiscoveryTimeout != null) { handler.removeCallbacks(kodiDiscoveryTimeout); kodiDiscoveryTimeout = null; }
        AlertDialog searching = discoveryDialog; discoveryDialog = null;
        if (searching.isShowing()) searching.dismiss();
        if (resolvedKodiEndpoints.isEmpty()) {
            new AlertDialog.Builder(this).setTitle("No Kodi found")
                    .setMessage("Check that Kodi and this device are on the same network, Zeroconf/service announcements are enabled in Kodi, and HTTP control is enabled. You can still enter the Kodi IP address manually.")
                    .setPositiveButton("OK", null).show();
            settingsMessage("No Kodi HTTP JSON-RPC service found. Manual connection is still available.", MUTED);
            return;
        }
        String[] labels = new String[resolvedKodiEndpoints.size()];
        for (int i = 0; i < labels.length; i++) {
            KodiEndpoint endpoint = resolvedKodiEndpoints.get(i);
            labels[i] = endpoint.name + "\n" + endpoint.host + ":" + endpoint.port + " · Discovered, not yet verified";
        }
        new AlertDialog.Builder(this).setTitle("Kodi devices found")
                .setItems(labels, (dialog, which) -> verifyKodiCandidate(resolvedKodiEndpoints.get(which)))
                .setNegativeButton("Cancel", null).show();
    }

    private void verifyKodiCandidate(KodiEndpoint endpoint) {
        final EditText hostField = discoveryHostField, portField = discoveryPortField;
        final EditText usernameField = discoveryUsernameField, passwordField = discoveryPasswordField;
        final String username = usernameField == null ? prefs.getString("user", "") : usernameField.getText().toString();
        final String password = passwordField == null ? prefs.getString("pass", "") : passwordField.getText().toString();
        settingsMessage("Checking " + endpoint.name + "…", MUTED);
        userRequestExecutor().execute(() -> {
            String kodiName = endpoint.name; String failure = null;
            try {
                KodiClient candidate = new KodiClient(endpoint.host, endpoint.port, username, password);
                candidate.ping();
                JSONObject app = candidate.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("name")));
                kodiName = app.optString("name", endpoint.name);
            } catch (Exception e) { failure = safeMessage(e); }
            final String verifiedName = kodiName, problem = failure;
            handler.post(() -> {
                if (destroyed || !inSettings) return;
                if (problem != null) {
                    settingsMessage("Could not verify " + endpoint.name + ": " + problem, RED);
                    new AlertDialog.Builder(this).setTitle("Kodi did not respond")
                            .setMessage(problem + "\n\nYour saved Kodi connection was not changed. Check the existing username/password fields or use manual settings.")
                            .setPositiveButton("OK", null).show();
                    return;
                }
                new AlertDialog.Builder(this).setTitle("Use this Kodi?")
                        .setMessage(verifiedName + "\n" + endpoint.host + ":" + endpoint.port + "\n\nChoose Use and Save to replace the current connection settings.")
                        .setNegativeButton("Cancel", null)
                        .setPositiveButton("Use and Save", (dialog, which) -> {
                            if (hostField != null && portField != null && usernameField != null && passwordField != null) {
                                hostField.setText(endpoint.host); portField.setText(endpoint.port);
                                saveConnection(hostField, portField, usernameField, passwordField);
                            } else {
                                prefs.edit().putString("host", endpoint.host).putString("port", endpoint.port).apply();
                                connected = true; settingsMessage("Kodi connection saved · " + verifiedName, GREEN); checkKodiNow();
                            }
                        }).show();
            });
        });
    }

    private String safeMessage(Exception e) { return e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage(); }

    private void saveConnection(EditText host, EditText port, EditText username, EditText password) {
        String h = host.getText().toString().trim(), p = port.getText().toString().trim();
        if (h.isEmpty()) { settingsMessage("Ange Kodi-värdens IP-adress eller värdnamn.", RED); return; }
        try { int number = Integer.parseInt(p); if (number < 1 || number > 65535) throw new NumberFormatException(); }
        catch (Exception e) { settingsMessage("Porten måste vara ett tal mellan 1 och 65535.", RED); return; }
        // Same preference keys as 0.1, so in-place APK update preserves existing saved settings.
        prefs.edit().putString("host", h).putString("port", p).putString("user", username.getText().toString()).putString("pass", password.getText().toString()).apply();
        settingsMessage("Connection settings saved", GREEN); checkKodiNow();
    }

    private void openWifiSettings() {
        try { startActivity(new android.content.Intent(android.provider.Settings.ACTION_WIFI_SETTINGS)); }
        catch (Exception e) { settingsMessage("Android Wi-Fi Settings is not available on this firmware.", RED); }
    }

    private void settingsMessage(String value, int color) { if (settingsFeedback != null) { settingsFeedback.setText(value == null ? "Connection failed" : value); settingsFeedback.setTextColor(color); } else Toast.makeText(this, value, Toast.LENGTH_SHORT).show(); }

    private EditText edit(String value, String hint, int inputType) {
        EditText e = new EditText(this); e.setSingleLine(true); e.setText(value); e.setHint(hint); e.setTextColor(TEXT); e.setHintTextColor(MUTED); e.setTextSize(14); e.setInputType(inputType); e.setPadding(dp(10), 0, dp(10), 0); e.setBackgroundResource(R.drawable.settings_input_background); e.setSelectAllOnFocus(false);
        e.setOnFocusChangeListener((view, focused) -> {
            if (focused && settingsScroll != null) e.postDelayed(() -> {
                Rect rect = new Rect(0, 0, e.getWidth(), e.getHeight()); settingsScroll.requestChildRectangleOnScreen(e, rect, true);
            }, 250);
        });
        return e;
    }
    private LinearLayout.LayoutParams fullField() { LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, dp(50)); lp.topMargin = dp(1); lp.bottomMargin = dp(2); return lp; }
    private void actionButton(LinearLayout parent, int iconRes, String label, boolean primary, Runnable action) {
        View button = makeActionButton(iconRes, label, primary, action);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(48), 1); lp.setMargins(dp(3), dp(4), dp(3), dp(4)); parent.addView(button, lp);
    }

    private LinearLayout makeActionButton(int iconRes, String label, boolean primary, Runnable action) {
        LinearLayout button = new LinearLayout(this); button.setOrientation(LinearLayout.HORIZONTAL); button.setGravity(Gravity.CENTER); button.setPadding(dp(8), 0, dp(8), 0);
        button.setBackgroundResource(primary ? R.drawable.settings_button_primary : R.drawable.settings_button_secondary); button.setContentDescription(label);
        ImageView icon = settingsIcon(iconRes, null); button.addView(icon, new LinearLayout.LayoutParams(dp(18), dp(18)));
        TextView caption = text(label, 12, TEXT, true); caption.setGravity(Gravity.CENTER); LinearLayout.LayoutParams captionLp = new LinearLayout.LayoutParams(-2, -1); captionLp.leftMargin = dp(5); button.addView(caption, captionLp);
        button.setOnClickListener(v -> action.run()); return button;
    }

    private void showStreams(boolean audio) {
        if (activePlayerId < 0) { toast("Starta uppspelning i Kodi för att välja spår."); return; }
        userRequestExecutor().execute(() -> {
            try {
                KodiClient c = client();
                JSONObject props = c.call("Player.GetProperties", new JSONObject().put("playerid", activePlayerId).put("properties", new JSONArray().put(audio ? "audiostreams" : "subtitles").put(audio ? "currentaudiostream" : "currentsubtitle").put("subtitleenabled")));
                JSONArray tracks = props.optJSONArray(audio ? "audiostreams" : "subtitles"); if (tracks == null) tracks = new JSONArray();
                JSONObject current = props.optJSONObject(audio ? "currentaudiostream" : "currentsubtitle"); int selected = current == null ? -1 : current.optInt("index", -1);
                JSONArray finalTracks = tracks; int selectedTrack = selected;
                handler.post(() -> presentTracks(audio, finalTracks, selectedTrack));
            } catch (Exception e) { handler.post(() -> toast(e.getMessage())); }
        });
    }

    private void presentTracks(boolean audio, JSONArray streams, int selected) {
        if (streams.length() == 0 && audio) { toast("Inga ljudspår rapporteras för den här Kodi-spelaren."); return; }
        if (streams.length() == 0 && !audio) { toast("Inga undertextspår rapporteras för den här Kodi-spelaren."); return; }
        String[] labels = new String[streams.length() + (audio ? 0 : 1)]; int[] streamIds = new int[labels.length]; int offset = audio ? 0 : 1;
        if (!audio) labels[0] = "Off";
        int checked = audio ? -1 : (isSubtitlesOff() ? 0 : -1);
        for (int i = 0; i < streams.length(); i++) {
            JSONObject stream = streams.optJSONObject(i); int streamId = stream == null ? i : stream.optInt("index", i);
            labels[i + offset] = KodiClient.streamLabel(stream, streamId, audio ? "Audio" : "Subtitle"); streamIds[i + offset] = streamId;
            if (streamId == selected) checked = i + offset;
        }
        if (audio && streams.length() == 1) { toast("Only one audio track is available: " + labels[0]); return; }
        final int[] ids = streamIds;
        new AlertDialog.Builder(this).setTitle(audio ? "Audio" : "Subtitles").setSingleChoiceItems(labels, checked, (dialog, which) -> {
            int index = !audio && which == 0 ? -1 : ids[which];
            chooseStream(audio, index); dialog.dismiss();
        }).setNegativeButton("Cancel", null).show();
    }

    private boolean isSubtitlesOff() { return subsValue != null && "Subtitles: Off".contentEquals(subsValue.getText()); }
    private void chooseStream(boolean audio, int index) {
        action(c -> {
            JSONObject p = new JSONObject(); p.put("playerid", activePlayerId);
            if (audio) { p.put("stream", index); return c.call("Player.SetAudioStream", p); }
            if (index < 0) { p.put("subtitle", "off"); p.put("enable", false); }
            else { p.put("subtitle", index); p.put("enable", true); }
            return c.call("Player.SetSubtitle", p);
        });
    }

    private void back() { action(c -> c.call("Input.Back", new JSONObject())); }
    private void playPause() { action(c -> { if (activePlayerId < 0) return c.call("Input.ExecuteAction", new JSONObject().put("action", "playpause")); return c.call("Player.PlayPause", new JSONObject().put("playerid", activePlayerId)); }); }
    private void stop() { action(c -> { if (activePlayerId < 0) throw new KodiClient.KodiException("Ingen aktiv Kodi-spelare."); return c.call("Player.Stop", new JSONObject().put("playerid", activePlayerId)); }); }
    private void confirmKodiShutdown() {
        if (kodiShutdownRequested) { toast("Kodi shutdown has already been requested."); return; }
        new AlertDialog.Builder(this)
                .setTitle("Power off Kodi?")
                .setMessage("This will close Kodi and shut down the Kodi device. The Android remote will stay on.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Power Off", (dialog, which) -> powerOffKodi())
                .show();
    }

    private void powerOffKodi() {
        if (kodiShutdownRequested) return;
        kodiShutdownRequested = true;
        userRequestExecutor().execute(() -> {
            try {
                client().call("System.Shutdown", new JSONObject());
                handler.post(() -> {
                    connected = false; activePlayerId = -1; updateHeader(); resetPlayer();
                    setStatus("OFFLINE · Kodi is shutting down");
                    toast("Shutdown command sent to the Kodi device.");
                });
            } catch (Exception e) {
                handler.post(() -> {
                    kodiShutdownRequested = false;
                    toast("Could not power off Kodi: " + (e.getMessage() == null ? "Kodi did not accept the shutdown request." : e.getMessage()));
                });
            }
        });
    }
    private void seekStep(String step) { action(c -> { if (activePlayerId < 0) throw new KodiClient.KodiException("Ingen aktiv Kodi-spelare."); return c.call("Player.Seek", new JSONObject().put("playerid", activePlayerId).put("value", new JSONObject().put("step", step))); }); }
    private void goTo(String to) { action(c -> { if (activePlayerId < 0) throw new KodiClient.KodiException("Ingen aktiv Kodi-spelare."); return c.call("Player.GoTo", new JSONObject().put("playerid", activePlayerId).put("to", to)); }); }
    private void seekPercent(double value) { action(c -> { if (activePlayerId < 0) throw new KodiClient.KodiException("Ingen aktiv Kodi-spelare."); return c.call("Player.Seek", new JSONObject().put("playerid", activePlayerId).put("value", new JSONObject().put("percentage", Math.max(0, Math.min(100, value))))); }); }
    private void activate(String window, String[] parameters) { action(c -> { JSONObject p = new JSONObject().put("window", window); if (parameters != null) p.put("parameters", new JSONArray(parameters)); return c.call("GUI.ActivateWindow", p); }); }

    private void adjustVolume(int delta) {
        action(c -> {
            JSONObject current = c.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("volume")));
            int value = Math.max(0, Math.min(100, current.optInt("volume", 0) + delta));
            return c.call("Application.SetVolume", new JSONObject().put("volume", value));
        });
    }
    private void toggleMute() {
        action(c -> c.call("Application.SetMute", new JSONObject().put("mute", "toggle")));
    }

    private interface KodiAction { JSONObject run(KodiClient client) throws Exception; }
    private void action(KodiAction request) {
        haptic();
        userRequestExecutor().execute(() -> { try { KodiClient client = client(); request.run(client); handler.post(() -> { connected = true; updateHeader(); if (isDedicatedOs()) { consecutivePollFailures = 0; schedulePoll(0); } }); }
            catch (Exception e) { handler.post(() -> { connected = false; updateHeader(); toast(e.getMessage() == null ? "Kodi-åtgärden misslyckades." : e.getMessage()); if (isDedicatedOs() && prefs.getBoolean("auto_reconnect", true)) { consecutivePollFailures++; schedulePoll(reconnectDelayMs()); } }); } });
    }

    private KodiClient client() throws KodiClient.KodiException {
        return new KodiClient(prefs.getString("host", ""), prefs.getString("port", "8080"), prefs.getString("user", ""), prefs.getString("pass", ""));
    }

    private void checkKodiNow() {
        userRequestExecutor().execute(() -> { try { KodiClient c = client(); JSONObject result = c.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("name"))); handler.post(() -> { connected = true; consecutivePollFailures = 0; if (hostLabel != null) hostLabel.setText(result.optString("name", prefs.getString("host", "Kodi"))); updateHeader(); if (isDedicatedOs()) schedulePoll(0); }); }
            catch (Exception e) { handler.post(() -> { connected = false; updateHeader(); }); } });
    }

    private final Runnable poll = new Runnable() {
        @Override public void run() {
            if (destroyed || !activityStarted) return;
            if (isDedicatedOs() && (!screenIsOn || inSettings)) return;
            if (busy) { if (!isDedicatedOs()) schedulePoll(3000); return; }
            if (!isDedicatedOs() && (inSettings || (!prefs.getBoolean("auto_reconnect", true) && !connected))) { schedulePoll(3000); return; }
            if (isDedicatedOs() && !prefs.getBoolean("auto_reconnect", true) && !connected) return;
            busy = true;
            final long startedAt = android.os.SystemClock.elapsedRealtime();
            if (isDedicatedOs()) android.util.Log.d("FarfarRemoteBattery", "poll_start mode=" + prefs.getString("os_battery_mode", "normal"));
            io.execute(() -> {
                KodiClient.Snapshot snapshot = null; String error = null;
                try { snapshot = client().snapshot(); } catch (Exception e) { error = e.getMessage(); android.util.Log.w("FarfarRemote", "Kodi poll failed: " + e.getMessage()); }
                final KodiClient.Snapshot result = snapshot; final String message = error;
                if (isDedicatedOs()) android.util.Log.d("FarfarRemoteBattery", "poll_end duration_ms=" + (android.os.SystemClock.elapsedRealtime() - startedAt) + " connected=" + (result != null) + " player=" + (result != null && result.player != null));
                handler.post(() -> {
                    busy = false;
                    if (!activityStarted || (isDedicatedOs() && !screenIsOn)) return;
                    if (!inSettings) {
                        if (result != null) { consecutivePollFailures = 0; applySnapshot(result); }
                        else {
                            consecutivePollFailures++;
                            connected = false; activePlayerId = -1; setStatus("OFFLINE · " + (message == null ? "Kodi unreachable" : message)); updateHeader(); resetPlayer();
                        }
                    }
                    long next = isDedicatedOs() ? osPollDelayMs(result) : 2800;
                    if (next >= 0) schedulePoll(next);
                });
            });
        }
    };

    private long reconnectDelayMs() {
        int exponent = Math.max(0, Math.min(4, consecutivePollFailures - 1));
        return Math.min(30000L, 2000L << exponent);
    }

    private long osPollDelayMs(KodiClient.Snapshot result) {
        if (!connected) return prefs.getBoolean("auto_reconnect", true) ? reconnectDelayMs() : -1;
        String profile = prefs.getString("os_battery_mode", "normal");
        if ("normal".equals(profile)) return 2800;
        if (android.os.SystemClock.elapsedRealtime() - lastBatteryInteractionMs < 12000) return 2800;
        boolean playing = result != null ? result.player != null : activePlayerId >= 0;
        if (playing) return "maximum".equals(profile) ? 10000 : 5000;
        String seconds = prefs.getString("os_battery_idle_seconds", "5");
        if ("2".equals(seconds)) return 2000;
        if ("10".equals(seconds)) return 10000;
        return 5000;
    }

    private void schedulePoll(long delayMs) {
        handler.removeCallbacks(poll);
        if (activityStarted && !destroyed && (!isDedicatedOs() || (screenIsOn && !inSettings))) handler.postDelayed(poll, Math.max(0, delayMs));
    }

    private void applySnapshot(KodiClient.Snapshot s) {
        connected = s.connected; hostLabel.setText(s.hostLabel == null ? prefs.getString("host", "Kodi") : s.hostLabel);
        updateHeader();
        if (status != null) { status.setText(s.error != null ? "CONNECTED · PLAYER STATUS LIMITED" : "CONNECTED · " + s.volume + "%" + (s.muted ? " · MUTED" : "")); status.setTextColor(GREEN); }
        KodiClient.PlayerState p = s.player;
        if (p == null) { activePlayerId = -1; resetPlayer(); return; }
        activePlayerId = p.id;
        if (titleText != null) titleText.setText(p.title);
        if (episodeText != null) episodeText.setText(p.subtitle.isEmpty() ? "Kodi playback" : p.subtitle);
        if (stateText != null) { stateText.setText(p.speed == 0 ? "PAUSED" : p.speed < 0 ? "REWIND" : p.speed > 1 ? "PLAYING · " + p.speed + "×" : "PLAYING"); stateText.setTextColor(p.speed == 0 ? CYAN : GREEN); }
        if (elapsedText != null) elapsedText.setText(p.elapsed);
        if (durationText != null) durationText.setText(p.duration);
        if (progress != null && !draggingSeek) { progress.setProgress((int) Math.round(p.percentage * 10)); progress.setEnabled(p.canSeek); }
        JSONObject a = p.currentAudio >= 0 && p.currentAudio < p.audioStreams.length() ? p.audioStreams.optJSONObject(p.currentAudio) : null;
        JSONObject sub = p.currentSubtitle >= 0 && p.currentSubtitle < p.subtitleStreams.length() ? p.subtitleStreams.optJSONObject(p.currentSubtitle) : null;
        if (audioValue != null) audioValue.setText("Audio: " + (a == null ? "—" : KodiClient.streamLabel(a, p.currentAudio, "Audio")));
        if (subsValue != null) subsValue.setText("Subtitles: " + (!p.subtitleEnabled || sub == null ? "Off" : KodiClient.streamLabel(sub, p.currentSubtitle, "Subtitle")));
        if (!p.thumbnail.equals(currentArtwork)) loadArtwork(p.thumbnail);
    }

    private void resetPlayer() {
        if (titleText != null) titleText.setText("Nothing playing"); if (episodeText != null) episodeText.setText("Kodi is ready when you are");
        if (stateText != null) { stateText.setText("IDLE"); stateText.setTextColor(MUTED); }
        if (elapsedText != null) elapsedText.setText("0:00"); if (durationText != null) durationText.setText("0:00");
        if (audioValue != null) audioValue.setText("Audio: —"); if (subsValue != null) subsValue.setText("Subtitles: Off");
        if (progress != null) { progress.setProgress(0); progress.setEnabled(false); }
        if (poster != null) poster.setImageResource(R.drawable.placeholder_art);
    }

    private void loadArtwork(String thumbnail) {
        currentArtwork = thumbnail;
        if (thumbnail == null || thumbnail.isEmpty()) { if (poster != null) poster.setImageResource(R.drawable.placeholder_art); return; }
        final String path = KodiClient.imageUrl(prefs.getString("host", ""), prefs.getString("port", "8080"), thumbnail);
        io.execute(() -> {
            Bitmap bitmap = null; HttpURLConnection c = null;
            try {
                c = (HttpURLConnection) new URL(path).openConnection(); c.setConnectTimeout(2200); c.setReadTimeout(2600);
                String user = prefs.getString("user", ""), pass = prefs.getString("pass", "");
                if (!user.isEmpty()) c.setRequestProperty("Authorization", "Basic " + android.util.Base64.encodeToString((user + ":" + pass).getBytes("UTF-8"), android.util.Base64.NO_WRAP));
                InputStream in = c.getInputStream(); ByteArrayOutputStream bytes = new ByteArrayOutputStream(); byte[] buf = new byte[4096]; int n, total = 0;
                while ((n = in.read(buf)) != -1 && total < 2 * 1024 * 1024) { bytes.write(buf, 0, n); total += n; } in.close();
                byte[] data = bytes.toByteArray(); BitmapFactory.Options options = new BitmapFactory.Options(); options.inJustDecodeBounds = true; BitmapFactory.decodeByteArray(data, 0, data.length, options);
                options.inSampleSize = Math.max(1, Math.max(options.outWidth / 256, options.outHeight / 256)); options.inJustDecodeBounds = false; options.inPreferredConfig = Bitmap.Config.RGB_565;
                bitmap = BitmapFactory.decodeByteArray(data, 0, data.length, options);
            } catch (Exception ignored) { } finally { if (c != null) c.disconnect(); }
            final Bitmap result = bitmap;
            handler.post(() -> { if (!destroyed && poster != null && thumbnail.equals(currentArtwork)) { if (result != null) { if (artwork != null && !artwork.isRecycled()) artwork.recycle(); artwork = result; poster.setImageBitmap(result); } else poster.setImageResource(R.drawable.placeholder_art); } });
        });
    }

    private void updateHeader() {
        if (status != null && connected) { status.setText("CONNECTED"); status.setTextColor(GREEN); }
        else if (status != null) { status.setText("OFFLINE · Settings"); status.setTextColor(RED); }
        if (settingsKodiStatus != null) { settingsKodiStatus.setText(connected ? "Connected" : "Offline"); settingsKodiStatus.setTextColor(connected ? GREEN : RED); }
    }

    private void setStatus(String value) {
        if (status != null) { status.setText(value); status.setTextColor(value != null && value.startsWith("OFFLINE") ? RED : GREEN); }
    }

    private void toast(String value) { if (value != null && !isFinishing()) Toast.makeText(this, value, Toast.LENGTH_SHORT).show(); }
    private void haptic() { if (prefs.getBoolean("haptics", false)) { try { Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE); if (v != null && v.hasVibrator()) v.vibrate(18); } catch (Exception ignored) { } } }

    private LinearLayout row(LinearLayout parent) { LinearLayout r = new LinearLayout(this); r.setOrientation(LinearLayout.HORIZONTAL); r.setGravity(Gravity.CENTER_VERTICAL); LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2); p.topMargin = dp(3); p.bottomMargin = dp(3); parent.addView(r, p); return r; }
    private LinearLayout column() { LinearLayout l = new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); return l; }
    private TextView text(String value, int size, int color, boolean bold) { TextView t = new TextView(this); t.setText(value); t.setTextSize(size); t.setTextColor(color); if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD); t.setGravity(Gravity.CENTER_VERTICAL); return t; }
    private GradientDrawable panel() { GradientDrawable d = round(PANEL, dp(13)); d.setStroke(dp(1), Color.rgb(42, 75, 105)); return d; }
    private GradientDrawable round(int color, int radius) { GradientDrawable d = new GradientDrawable(GradientDrawable.Orientation.TL_BR, new int[]{Color.rgb(18, 35, 54), color}); d.setCornerRadius(radius); d.setStroke(dp(1), Color.rgb(33, 67, 97)); return d; }
    private int dp(int value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }

    @Override public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        if (!inSettings) buildScreen();
        else if (settingsScroll != null) { settingsScroll.setBackgroundResource(newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE ? R.drawable.settings_bg_landscape : R.drawable.settings_bg_portrait); settingsScroll.requestLayout(); }
    }

    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        noteBatteryInteraction();
        switch (keyCode) {
            case KeyEvent.KEYCODE_DPAD_UP: action(c -> c.call("Input.Up", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_DOWN: action(c -> c.call("Input.Down", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_LEFT: action(c -> c.call("Input.Left", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_RIGHT: action(c -> c.call("Input.Right", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_CENTER: case KeyEvent.KEYCODE_ENTER: action(c -> c.call("Input.Select", new JSONObject())); return true;
            case KeyEvent.KEYCODE_BACK: if (inSettings) { closeSettings(); return true; } if (!getResources().getBoolean(R.bool.dedicated_os)) return super.onKeyDown(keyCode, event); back(); return true;
            case KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE: playPause(); return true;
            case KeyEvent.KEYCODE_MEDIA_STOP: stop(); return true;
            case KeyEvent.KEYCODE_MEDIA_NEXT: goTo("next"); return true;
            case KeyEvent.KEYCODE_MEDIA_PREVIOUS: goTo("previous"); return true;
            case KeyEvent.KEYCODE_MEDIA_REWIND: seekStep("bigbackward"); return true;
            case KeyEvent.KEYCODE_MEDIA_FAST_FORWARD: seekStep("bigforward"); return true;
            case KeyEvent.KEYCODE_VOLUME_UP: adjustVolume(10); return true;
            case KeyEvent.KEYCODE_VOLUME_DOWN: adjustVolume(-10); return true;
            case KeyEvent.KEYCODE_VOLUME_MUTE: toggleMute(); return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override protected void onStart() {
        super.onStart(); activityStarted = true; updateSettingsBackCallback();
        if (isDedicatedOs()) {
            android.os.PowerManager power = (android.os.PowerManager) getSystemService(Context.POWER_SERVICE);
            screenIsOn = power == null || power.isScreenOn();
            try { IntentFilter filter = new IntentFilter(); filter.addAction(Intent.ACTION_SCREEN_ON); filter.addAction(Intent.ACTION_SCREEN_OFF); registerReceiver(screenStateReceiver, filter); screenReceiverRegistered = true; }
            catch (Exception e) { android.util.Log.w("FarfarRemoteBattery", "Could not register screen-state receiver", e); }
        }
        handler.removeCallbacks(poll);
        if (!isDedicatedOs() || (screenIsOn && !inSettings)) handler.post(poll);
    }
    @Override protected void onStop() {
        activityStarted = false; handler.removeCallbacks(poll); stopKodiDiscovery(true);
        if (screenReceiverRegistered) { try { unregisterReceiver(screenStateReceiver); } catch (Exception ignored) { } screenReceiverRegistered = false; }
        if (settingsBackCallback != null) { Api33BackHandler.unregister(this, settingsBackCallback); settingsBackCallback = null; }
        super.onStop();
    }
    @Override protected void onDestroy() { stopKodiDiscovery(true); destroyed = true; handler.removeCallbacksAndMessages(null); io.shutdownNow(); commands.shutdownNow(); if (artwork != null && !artwork.isRecycled()) artwork.recycle(); super.onDestroy(); }
}
