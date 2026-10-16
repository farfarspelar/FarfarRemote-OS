package org.farfarremote;

import android.net.Uri;
import android.util.Base64;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.net.UnknownHostException;

/** Small synchronous JSON-RPC client. Call only from the app's single I/O executor. */
final class KodiClient {
    static final class KodiException extends Exception {
        KodiException(String message) { super(message); }
    }

    static final class PlayerState {
        int id;
        String title = "Nothing playing";
        String subtitle = "";
        String thumbnail = "";
        String file = "";
        String elapsed = "0:00";
        String duration = "0:00";
        String mediaType = "";
        String seriesTitle = "";
        String plot = "";
        String plotOutline = "";
        String genres = "";
        String year = "";
        String director = "";
        String studio = "";
        String rating = "";
        String contentRating = "";
        String imdbId = "";
        String tagline = "";
        double percentage;
        int speed;
        boolean canSeek;
        boolean subtitleEnabled;
        int currentAudio = -1;
        int currentSubtitle = -1;
        JSONArray audioStreams = new JSONArray();
        JSONArray subtitleStreams = new JSONArray();
    }

    static final class Snapshot {
        boolean connected;
        String hostLabel;
        String error;
        String volume = "--";
        boolean muted;
        PlayerState player;
    }

    private final String host;
    private final int port;
    private final String username;
    private final String password;
    private int nextId = 1;

    private static JSONObject json(Object... pairs) {
        JSONObject out = new JSONObject();
        try { for (int i = 0; i + 1 < pairs.length; i += 2) out.put(String.valueOf(pairs[i]), pairs[i + 1]); }
        catch (Exception e) { throw new IllegalArgumentException("Invalid JSON-RPC parameters", e); }
        return out;
    }

    KodiClient(String host, String port, String username, String password) throws KodiException {
        this.host = cleanHost(host);
        try { this.port = Integer.parseInt(port.trim()); }
        catch (Exception e) { throw new KodiException("Porten måste vara ett tal mellan 1 och 65535."); }
        if (this.port < 1 || this.port > 65535) throw new KodiException("Porten måste vara mellan 1 och 65535.");
        if (this.host.length() == 0) throw new KodiException("Ange Kodi-värdens IP-adress eller värdnamn i Settings.");
        this.username = username == null ? "" : username;
        this.password = password == null ? "" : password;
    }

    private static String cleanHost(String value) throws KodiException {
        String h = value == null ? "" : value.trim();
        if (h.startsWith("http://")) h = h.substring(7);
        else if (h.startsWith("https://")) throw new KodiException("Använd Kodis HTTP-värdnamn/IP utan https-prefix.");
        int slash = h.indexOf('/');
        if (slash >= 0) h = h.substring(0, slash);
        if (h.indexOf('@') >= 0 || h.indexOf(' ') >= 0) throw new KodiException("Ange bara ett värdnamn eller en IP-adress.");
        if (h.startsWith("[") && h.endsWith("]")) h = h.substring(1, h.length() - 1);
        return h;
    }

    private String endpoint() {
        String h = host.indexOf(':') >= 0 ? "[" + host + "]" : host;
        return "http://" + h + ":" + port + "/jsonrpc";
    }

    JSONObject call(String method, JSONObject params) throws KodiException {
        Object result = callRaw(method, params);
        return result instanceof JSONObject ? (JSONObject) result : new JSONObject();
    }

    JSONArray callArray(String method, JSONObject params) throws KodiException {
        Object result = callRaw(method, params);
        return result instanceof JSONArray ? (JSONArray) result : new JSONArray();
    }

    private Object callRaw(String method, JSONObject params) throws KodiException {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(endpoint()).openConnection();
            c.setConnectTimeout(2300); c.setReadTimeout(2800); c.setRequestMethod("POST"); c.setDoOutput(true);
            c.setUseCaches(false); c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            if (!username.isEmpty()) c.setRequestProperty("Authorization", "Basic " + Base64.encodeToString((username + ":" + password).getBytes("UTF-8"), Base64.NO_WRAP));
            JSONObject request = new JSONObject();
            request.put("jsonrpc", "2.0"); request.put("id", nextId++); request.put("method", method); request.put("params", params == null ? new JSONObject() : params);
            byte[] payload = request.toString().getBytes("UTF-8"); c.setFixedLengthStreamingMode(payload.length);
            OutputStream out = c.getOutputStream(); out.write(payload); out.close();
            int code = c.getResponseCode();
            if (code == 401 || code == 403) throw new KodiException("Kodi nekände inte användarnamn/lösenord (HTTP " + code + ").");
            InputStream in = code >= 400 ? c.getErrorStream() : c.getInputStream();
            if (in == null) throw new KodiException("Kodi svarade HTTP " + code + " utan JSON-svar.");
            ByteArrayOutputStream bytes = new ByteArrayOutputStream(); byte[] buffer = new byte[1024]; int n;
            while ((n = in.read(buffer)) != -1) bytes.write(buffer, 0, n); in.close();
            if (code < 200 || code >= 300) throw new KodiException("Kodi svarade HTTP " + code + ". Kontrollera JSON-RPC/Webserver i Kodi.");
            JSONObject response = new JSONObject(new String(bytes.toByteArray(), "UTF-8"));
            if (response.has("error")) {
                JSONObject error = response.optJSONObject("error");
                throw new KodiException(error == null ? "Kodi JSON-RPC-fel." : error.optString("message", "Kodi JSON-RPC-fel."));
            }
            return response.opt("result");
        } catch (KodiException e) { throw e; }
        catch (UnknownHostException e) { throw new KodiException("Kodi-värdnamnet kunde inte hittas. Kontrollera adress och Wi-Fi."); }
        catch (SocketTimeoutException e) { throw new KodiException("Kodi svarar inte ännu (timeout). Kontrollera värd, port och nätverk."); }
        catch (java.net.ConnectException e) { throw new KodiException("Kan inte ansluta till Kodi. Kontrollera IP, port och att Kodis fjärrstyrning är aktiverad."); }
        catch (Exception e) { throw new KodiException("Nätverksfel: " + (e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage())); }
        finally { if (c != null) c.disconnect(); }
    }

    JSONObject ping() throws KodiException { return call("JSONRPC.Ping", new JSONObject()); }

    String scanVideoLibrary(String directory) throws KodiException {
        JSONObject params = json("directory", directory, "showdialogs", false);
        Object result = callRaw("VideoLibrary.Scan", params);
        return result instanceof String ? (String) result : "OK";
    }

    Snapshot snapshot() throws KodiException { return snapshot(false); }

    Snapshot snapshot(boolean includeExtendedMediaDetails) throws KodiException {
        Snapshot state = new Snapshot();
        // A successful, widely supported one-property read is the connectivity signal.
        JSONObject app = call("Application.GetProperties", json("properties", new JSONArray().put("name")));
        state.connected = true; state.hostLabel = app.optString("name", host);
        if (state.hostLabel.length() == 0) state.hostLabel = host;
        try {
            JSONObject audio = call("Application.GetProperties", json("properties", new JSONArray().put("volume").put("muted")));
            state.volume = audio.has("volume") ? String.valueOf(audio.optInt("volume")) : "--"; state.muted = audio.optBoolean("muted", false);
        } catch (KodiException ignored) { state.volume = "--"; }
        JSONArray active;
        try { active = callArray("Player.GetActivePlayers", new JSONObject()); }
        catch (KodiException e) { state.error = e.getMessage(); android.util.Log.w("FarfarRemote", "Player list unavailable: " + e.getMessage()); return state; }
        if (active.length() == 0) return state;
        JSONObject activePlayer = active.optJSONObject(0); if (activePlayer == null) return state;
        PlayerState p = new PlayerState(); p.id = activePlayer.optInt("playerid", 0);
        JSONObject props; JSONObject itemResponse = new JSONObject();
        try {
            props = call("Player.GetProperties", json("playerid", p.id, "properties",
                    new JSONArray().put("time").put("totaltime").put("percentage").put("speed").put("canseek")));
        } catch (KodiException e) {
            state.error = e.getMessage(); state.player = p;
            android.util.Log.w("FarfarRemote", "Player progress unavailable: " + e.getMessage()); return state;
        }
        try {
            JSONObject audio = call("Player.GetProperties", json("playerid", p.id, "properties", new JSONArray().put("audiostreams").put("currentaudiostream")));
            p.audioStreams = audio.optJSONArray("audiostreams"); if (p.audioStreams == null) p.audioStreams = new JSONArray();
            JSONObject currentAudio = audio.optJSONObject("currentaudiostream"); if (currentAudio != null) p.currentAudio = currentAudio.optInt("index", -1);
        } catch (KodiException e) { state.error = e.getMessage(); android.util.Log.w("FarfarRemote", "Audio stream list unavailable: " + e.getMessage()); }
        try {
            JSONObject subtitles = call("Player.GetProperties", json("playerid", p.id, "properties", new JSONArray().put("subtitles").put("currentsubtitle").put("subtitleenabled")));
            p.subtitleStreams = subtitles.optJSONArray("subtitles"); if (p.subtitleStreams == null) p.subtitleStreams = new JSONArray();
            JSONObject currentSubtitle = subtitles.optJSONObject("currentsubtitle"); if (currentSubtitle != null) p.currentSubtitle = currentSubtitle.optInt("index", -1);
            p.subtitleEnabled = subtitles.optBoolean("subtitleenabled", false);
        } catch (KodiException e) { state.error = e.getMessage(); android.util.Log.w("FarfarRemote", "Subtitle stream list unavailable: " + e.getMessage()); }
        try {
            itemResponse = call("Player.GetItem", json("playerid", p.id, "properties",
                    new JSONArray().put("title").put("showtitle").put("episode").put("season").put("thumbnail").put("artist").put("album").put("file")));
        } catch (KodiException e) { state.error = e.getMessage(); android.util.Log.w("FarfarRemote", "Now Playing metadata unavailable: " + e.getMessage()); }
        JSONObject item = itemResponse.optJSONObject("item"); if (item == null) item = new JSONObject();
        // Keep the established Now Playing request intact for older Kodi JSON-RPC versions.
        // Extended scraped metadata is optional and must never make playback controls fail.
        if (includeExtendedMediaDetails) {
            try {
                JSONObject details = call("Player.GetItem", json("playerid", p.id, "properties",
                        new JSONArray().put("type").put("plot").put("plotoutline").put("genre").put("year")
                                .put("director").put("studio").put("rating").put("mpaa").put("imdbnumber").put("tagline")));
                JSONObject extended = details.optJSONObject("item");
                if (extended != null) item = mergeItems(item, extended);
            } catch (KodiException e) { android.util.Log.d("FarfarRemote", "Extended media details unavailable: " + e.getMessage()); }
        }
        String title = item.optString("title", "");
        if (title.length() == 0) title = item.optString("label", "");
        if (title.length() == 0) title = item.optString("showtitle", "");
        p.title = title.length() == 0 ? "Now Playing" : title;
        String show = item.optString("showtitle", "");
        p.seriesTitle = show;
        int episode = item.optInt("episode", 0), season = item.optInt("season", 0);
        p.subtitle = !show.isEmpty() && episode > 0 ? show + " · S" + twoDigits(season) + " E" + twoDigits(episode) : item.optString("artist", item.optString("album", ""));
        p.thumbnail = item.optString("thumbnail", "");
        p.file = item.optString("file", "");
        p.mediaType = item.optString("type", "");
        p.plot = item.optString("plot", ""); p.plotOutline = item.optString("plotoutline", "");
        p.genres = jsonList(item.opt("genre")); p.year = item.has("year") ? String.valueOf(item.optInt("year")) : "";
        p.director = jsonList(item.opt("director")); p.studio = jsonList(item.opt("studio"));
        p.rating = item.has("rating") ? String.valueOf(item.optDouble("rating", 0)) : "";
        p.contentRating = item.optString("mpaa", ""); p.tagline = item.optString("tagline", "");
        p.imdbId = item.optString("imdbnumber", "");
        if (p.imdbId.isEmpty()) {
            JSONObject ids = item.optJSONObject("uniqueid");
            if (ids != null) p.imdbId = ids.optString("imdb", "");
        }
        p.elapsed = formatTime(props.optJSONObject("time")); p.duration = formatTime(props.optJSONObject("totaltime"));
        p.percentage = Math.max(0, Math.min(100, props.optDouble("percentage", 0))); p.speed = props.optInt("speed", 1); p.canSeek = props.optBoolean("canseek", false);
        state.player = p;
        return state;
    }

    JSONObject getDirectory(String directory) throws KodiException {
        // Keep the request to Kodi's required parameter plus media only. Older Kodi JSON-RPC
        // schemas reject optional file properties that newer versions accept.
        try {
            return call("Files.GetDirectory", json("directory", directory, "media", "video"));
        } catch (KodiException videoModeError) {
            // Some Kodi paths (notably add-on and filesystem paths) are only enumerable in file mode.
            try {
                return call("Files.GetDirectory", json("directory", directory, "media", "files"));
            } catch (KodiException filesModeError) {
                throw new KodiException(videoModeError.getMessage() + " (Kodi file-mode fallback also failed: " + filesModeError.getMessage() + ")");
            }
        }
    }

    JSONObject getSources(String media) throws KodiException {
        return call("Files.GetSources", json("media", media));
    }

    private static JSONObject mergeItems(JSONObject base, JSONObject extra) {
        JSONObject merged = new JSONObject();
        try {
            JSONArray names = base.names();
            if (names != null) for (int i = 0; i < names.length(); i++) { String key = names.optString(i); merged.put(key, base.opt(key)); }
            names = extra.names();
            if (names != null) for (int i = 0; i < names.length(); i++) { String key = names.optString(i); merged.put(key, extra.opt(key)); }
        } catch (Exception ignored) { return extra; }
        return merged;
    }

    private static String jsonList(Object value) {
        if (value instanceof JSONArray) {
            JSONArray array = (JSONArray) value; StringBuilder out = new StringBuilder();
            for (int i = 0; i < array.length(); i++) {
                String item = array.optString(i, ""); if (item.isEmpty()) continue;
                if (out.length() > 0) out.append(", "); out.append(item);
            }
            return out.toString();
        }
        return value == null || value == JSONObject.NULL ? "" : String.valueOf(value);
    }

    String currentPlayingDirectory() throws KodiException {
        JSONArray active = callArray("Player.GetActivePlayers", new JSONObject());
        if (active.length() == 0) return "";
        JSONObject player = active.optJSONObject(0);
        if (player == null) return "";
        JSONObject response = call("Player.GetItem", json("playerid", player.optInt("playerid", 0),
                "properties", new JSONArray().put("file")));
        JSONObject item = response.optJSONObject("item");
        if (item == null) return "";
        String file = item.optString("file", "").trim();
        if (file.isEmpty()) return "";

        // Add-on URLs can carry playback parameters after '?'; they are not part of the folder path.
        int query = file.indexOf('?');
        if (query >= 0) file = file.substring(0, query);
        while (file.endsWith("/") && file.length() > file.indexOf("://") + 3) {
            file = file.substring(0, file.length() - 1);
        }
        int slash = file.lastIndexOf('/');
        int schemeEnd = file.indexOf("://");
        if (slash < 0 || slash <= (schemeEnd < 0 ? -1 : schemeEnd + 2)) return "";
        return file.substring(0, slash + 1);
    }

    static String imageUrl(String host, String port, String image) {
        if (image == null || image.length() == 0) return "";
        String h = host != null && host.indexOf(':') >= 0 && !host.startsWith("[") ? "[" + host + "]" : host;
        return "http://" + h + ":" + port + "/image/" + Uri.encode(image);
    }

    static String streamLabel(JSONObject stream, int index, String kind) {
        if (stream == null) return kind + " Track " + (index + 1);
        String language = stream.optString("language", "");
        String name = stream.optString("name", "");
        String codec = stream.optString("codec", "");
        String label = !name.isEmpty() ? name : !language.isEmpty() ? language : kind + " Track " + (index + 1);
        if (!codec.isEmpty() && !label.toLowerCase().contains(codec.toLowerCase())) label += " · " + codec.toUpperCase();
        int channels = stream.optInt("channels", 0); if (channels > 0 && "Audio".equals(kind)) label += " · " + channels + "ch";
        return label;
    }

    static String formatTime(JSONObject time) {
        if (time == null) return "0:00";
        int hours = time.optInt("hours", 0), minutes = time.optInt("minutes", 0), seconds = time.optInt("seconds", 0);
        return hours > 0 ? String.format(java.util.Locale.US, "%d:%02d:%02d", hours, minutes, seconds) : String.format(java.util.Locale.US, "%d:%02d", minutes, seconds);
    }
    private static String twoDigits(int value) { return value < 10 ? "0" + value : String.valueOf(value); }
}
