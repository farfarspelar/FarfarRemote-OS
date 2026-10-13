package org.farfarremote;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Vibrator;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.CheckBox;
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
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Remote UI and input/action layer. Network operations are serialized off the UI thread. */
public final class MainActivity extends Activity {
    private static final String PREFS = "farfarremote"; // Keep 0.1 preference file/key names for upgrade continuity.
    private static final String VERSION = "0.2.0";
    private static final int BG = Color.rgb(7, 15, 27), PANEL = Color.rgb(14, 28, 45), TEXT = Color.rgb(235, 243, 252), MUTED = Color.rgb(154, 177, 202), CYAN = Color.rgb(35, 170, 255), GREEN = Color.rgb(52, 222, 157), RED = Color.rgb(255, 112, 116);

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private FrameLayout screen;
    private boolean inSettings, busy, draggingSeek, destroyed;
    private boolean startupShown;
    private boolean connected;
    private int activePlayerId = -1;
    private String currentArtwork = "";
    private Bitmap artwork;

    private TextView status, hostLabel, titleText, episodeText, elapsedText, durationText, stateText, audioValue, subsValue, connectionNote, settingsFeedback, volumeValue;
    private ImageView poster;
    private SeekBar progress;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        applyOrientationPreference();
        applyKeepAwake();
        getWindow().getDecorView().setSystemUiVisibility(5894 | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
        buildScreen();
        handler.post(poll);
    }

    private void applyOrientationPreference() {
        String mode = prefs.getString("orientation", "portrait");
        if ("landscape".equals(mode)) setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        else if ("auto".equals(mode)) setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_SENSOR);
        else setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
    }

    private void applyKeepAwake() {
        if (prefs.getBoolean("keep_awake", true)) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    private void buildScreen() {
        inSettings = false;
        screen = new FrameLayout(this);
        screen.setBackgroundColor(BG);
        setContentView(screen);
        View content = isLandscape() ? buildLandscape() : buildPortrait();
        screen.addView(content, new FrameLayout.LayoutParams(-1, -1));
        if (!startupShown) { startupShown = true; showStartupOverlay(); }
        setStatus(connected ? "CONNECTED" : "Kodi offline · Settings to configure");
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
        ImageView settings = new ImageView(this); settings.setImageResource(R.drawable.action_settings); settings.setScaleType(ImageView.ScaleType.FIT_CENTER); settings.setContentDescription("Settings"); settings.setOnClickListener(v -> showSettings());
        LinearLayout.LayoutParams gear = new LinearLayout.LayoutParams(dp(48), dp(46)); gear.leftMargin = dp(6); header.addView(settings, gear);
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
        ImageView image = new ImageView(this); image.setImageResource(res); image.setScaleType(ImageView.ScaleType.FIT_CENTER); box.addView(image, new LinearLayout.LayoutParams(-1, dp(isLandscape() ? 54 : 48)));
        TextView caption = text(label, isLandscape() ? 9 : 9, MUTED, false); caption.setGravity(Gravity.CENTER); caption.setMaxLines(1); box.addView(caption);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -2, weight); lp.leftMargin = dp(1); lp.rightMargin = dp(1); parent.addView(box, lp);
        box.setOnLongClickListener(v -> false);
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
    }

    private void addImageOnlyControl(LinearLayout parent, int res, String label, Runnable action) {
        ImageView image = new ImageView(this); image.setImageResource(res); image.setScaleType(ImageView.ScaleType.FIT_CENTER); image.setContentDescription(label); image.setFocusable(true); image.setOnClickListener(v -> { haptic(); action.run(); });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(isLandscape() ? 67 : 72), 1f); lp.setMargins(dp(1), 0, dp(1), 0); parent.addView(image, lp);
    }

    private void showSettings() {
        inSettings = true;
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true); scroll.setVerticalScrollBarEnabled(false);
        LinearLayout root = column(); root.setPadding(dp(16), dp(12), dp(16), dp(18)); scroll.addView(root);
        LinearLayout top = row(root); top.setGravity(Gravity.CENTER_VERTICAL);
        TextView back = text("‹", 34, CYAN, true); back.setGravity(Gravity.CENTER); back.setOnClickListener(v -> buildScreen()); top.addView(back, new LinearLayout.LayoutParams(dp(48), dp(48)));
        TextView heading = text("Settings", 24, TEXT, true); top.addView(heading);
        section(root, "KODI CONNECTION");
        EditText host = edit(prefs.getString("host", ""), "Hostname / IP", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        root.addView(host, fullField());
        LinearLayout portRow = row(root);
        EditText port = edit(prefs.getString("port", "8080"), "Port", InputType.TYPE_CLASS_NUMBER); portRow.addView(port, new LinearLayout.LayoutParams(dp(108), dp(53)));
        EditText username = edit(prefs.getString("user", ""), "Username", InputType.TYPE_CLASS_TEXT); portRow.addView(username, new LinearLayout.LayoutParams(0, dp(53), 1));
        EditText password = edit(prefs.getString("pass", ""), "Password", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD); root.addView(password, fullField());
        CheckBox showPassword = check("Show password", false); root.addView(showPassword); showPassword.setOnCheckedChangeListener((button, checked) -> {
            int pos = password.getSelectionStart(); password.setInputType(checked ? InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD : InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD); password.setSelection(Math.max(0, pos));
        });
        LinearLayout actions = row(root);
        actionButton(actions, "Test connection", () -> testConnection(host, port, username, password));
        actionButton(actions, "Save", () -> saveConnection(host, port, username, password));
        actionButton(actions, "Wi-Fi Settings", this::openWifiSettings);
        settingsFeedback = text(connected ? "Kodi ansluten" : "Kodi offline · inställningar går att ändra offline", 12, connected ? GREEN : MUTED, false); root.addView(settingsFeedback);

        section(root, "DISPLAY");
        RadioGroup orientation = new RadioGroup(this); orientation.setOrientation(RadioGroup.HORIZONTAL);
        addOrientation(orientation, "Portrait", "portrait"); addOrientation(orientation, "Landscape", "landscape"); addOrientation(orientation, "Auto", "auto"); root.addView(orientation);
        selectOrientation(orientation, prefs.getString("orientation", "portrait"));
        orientation.setOnCheckedChangeListener((group, checkedId) -> {
            RadioButton selected = findViewById(checkedId); if (selected == null) return;
            String val = String.valueOf(selected.getTag()); prefs.edit().putString("orientation", val).apply(); applyOrientationPreference();
        });
        CheckBox awake = check("Keep screen awake", prefs.getBoolean("keep_awake", true)); root.addView(awake); awake.setOnCheckedChangeListener((b, checked) -> { prefs.edit().putBoolean("keep_awake", checked).apply(); applyKeepAwake(); });

        section(root, "REMOTE");
        CheckBox reconnect = check("Auto reconnect", prefs.getBoolean("auto_reconnect", true)); root.addView(reconnect); reconnect.setOnCheckedChangeListener((b, checked) -> prefs.edit().putBoolean("auto_reconnect", checked).apply());
        CheckBox haptics = check("Haptic feedback", prefs.getBoolean("haptics", false)); root.addView(haptics); haptics.setOnCheckedChangeListener((b, checked) -> prefs.edit().putBoolean("haptics", checked).apply());
        TextView hardware = text("Physical / Bluetooth controls: Android key events remain enabled. External HID mapping can be added without changing the Kodi action layer.", 12, MUTED, false); root.addView(hardware);

        section(root, "SYSTEM INFORMATION");
        String model = android.os.Build.MODEL, androidVersion = android.os.Build.VERSION.RELEASE + " (API " + android.os.Build.VERSION.SDK_INT + ")";
        String appVersion = VERSION; try { PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0); appVersion = info.versionName; } catch (Exception ignored) { }
        root.addView(text("FarfarRemote " + appVersion + "\nAndroid " + androidVersion + "\n" + model + "\nKodi: " + (connected ? "Connected" : "Offline"), 13, TEXT, false));
        screen.removeAllViews(); screen.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
    }

    private void addOrientation(RadioGroup group, String label, String tag) { RadioButton rb = new RadioButton(this); rb.setId(View.generateViewId()); rb.setText(label); rb.setTextColor(TEXT); rb.setTag(tag); group.addView(rb); }
    private void selectOrientation(RadioGroup group, String value) { for (int i = 0; i < group.getChildCount(); i++) { RadioButton rb = (RadioButton) group.getChildAt(i); if (value.equals(rb.getTag())) { rb.setChecked(true); return; } } }

    private void testConnection(EditText host, EditText port, EditText username, EditText password) {
        try {
            KodiClient client = new KodiClient(host.getText().toString(), port.getText().toString(), username.getText().toString(), password.getText().toString());
            settingsMessage("Testing connection…", MUTED);
            io.execute(() -> { String message; boolean ok;
                try { client.ping(); JSONObject app = client.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("name"))); String n = app.optString("name", "Kodi"); message = "Connected · " + n; ok = true; }
                catch (Exception e) { message = e.getMessage() == null ? "Kodi anslöt inte." : e.getMessage(); ok = false; }
                final String msg = message; final boolean success = ok; handler.post(() -> { connected = success; settingsMessage(msg, success ? GREEN : RED); updateHeader(); });
            });
        } catch (Exception e) { settingsMessage(e.getMessage(), RED); }
    }

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

    private void section(LinearLayout root, String title) { TextView t = text(title, 11, CYAN, true); LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2); lp.topMargin = dp(18); lp.bottomMargin = dp(4); root.addView(t, lp); }
    private EditText edit(String value, String hint, int inputType) { EditText e = new EditText(this); e.setSingleLine(true); e.setText(value); e.setHint(hint); e.setTextColor(TEXT); e.setHintTextColor(MUTED); e.setTextSize(14); e.setInputType(inputType); e.setPadding(dp(10), 0, dp(10), 0); e.setBackground(round(Color.rgb(17, 33, 51), dp(8))); return e; }
    private CheckBox check(String label, boolean checked) { CheckBox b = new CheckBox(this); b.setText(label); b.setTextColor(TEXT); b.setChecked(checked); b.setMinHeight(dp(44)); return b; }
    private LinearLayout.LayoutParams fullField() { LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, dp(53)); lp.topMargin = dp(2); lp.bottomMargin = dp(3); return lp; }
    private void actionButton(LinearLayout parent, String label, Runnable action) { TextView b = text(label, 13, TEXT, true); b.setGravity(Gravity.CENTER); b.setBackground(round(Color.rgb(18, 49, 75), dp(10))); b.setOnClickListener(v -> action.run()); LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(48), 1); lp.setMargins(dp(3), dp(5), dp(3), dp(5)); parent.addView(b, lp); }

    private void showStreams(boolean audio) {
        if (activePlayerId < 0) { toast("Starta uppspelning i Kodi för att välja spår."); return; }
        io.execute(() -> {
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
        io.execute(() -> { try { KodiClient client = client(); request.run(client); handler.post(() -> { connected = true; updateHeader(); }); }
            catch (Exception e) { handler.post(() -> { connected = false; updateHeader(); toast(e.getMessage() == null ? "Kodi-åtgärden misslyckades." : e.getMessage()); }); } });
    }

    private KodiClient client() throws KodiClient.KodiException {
        return new KodiClient(prefs.getString("host", ""), prefs.getString("port", "8080"), prefs.getString("user", ""), prefs.getString("pass", ""));
    }

    private void checkKodiNow() {
        io.execute(() -> { try { KodiClient c = client(); JSONObject result = c.call("Application.GetProperties", new JSONObject().put("properties", new JSONArray().put("name"))); handler.post(() -> { connected = true; if (hostLabel != null) hostLabel.setText(result.optString("name", prefs.getString("host", "Kodi"))); updateHeader(); }); }
            catch (Exception e) { handler.post(() -> { connected = false; updateHeader(); }); } });
    }

    private final Runnable poll = new Runnable() {
        @Override public void run() {
            if (destroyed) return;
            if (inSettings || (busy) || (!prefs.getBoolean("auto_reconnect", true) && !connected)) { handler.postDelayed(this, 3000); return; }
            busy = true;
            io.execute(() -> {
                KodiClient.Snapshot snapshot = null; String error = null;
                try { snapshot = client().snapshot(); } catch (Exception e) { error = e.getMessage(); android.util.Log.w("FarfarRemote", "Kodi poll failed: " + e.getMessage()); }
                final KodiClient.Snapshot result = snapshot; final String message = error;
                handler.post(() -> { busy = false; if (!inSettings) { if (result != null) applySnapshot(result); else { connected = false; activePlayerId = -1; setStatus("OFFLINE · " + (message == null ? "Kodi unreachable" : message)); updateHeader(); resetPlayer(); } } handler.postDelayed(this, 2800); });
            });
        }
    };

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

    @Override public void onConfigurationChanged(Configuration newConfig) { super.onConfigurationChanged(newConfig); if (!inSettings) buildScreen(); else showSettings(); }

    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        switch (keyCode) {
            case KeyEvent.KEYCODE_DPAD_UP: action(c -> c.call("Input.Up", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_DOWN: action(c -> c.call("Input.Down", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_LEFT: action(c -> c.call("Input.Left", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_RIGHT: action(c -> c.call("Input.Right", new JSONObject())); return true;
            case KeyEvent.KEYCODE_DPAD_CENTER: case KeyEvent.KEYCODE_ENTER: action(c -> c.call("Input.Select", new JSONObject())); return true;
            case KeyEvent.KEYCODE_BACK: if (inSettings) { buildScreen(); return true; } back(); return true;
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

    @Override protected void onDestroy() { destroyed = true; handler.removeCallbacksAndMessages(null); io.shutdownNow(); if (artwork != null && !artwork.isRecycled()) artwork.recycle(); super.onDestroy(); }
}
