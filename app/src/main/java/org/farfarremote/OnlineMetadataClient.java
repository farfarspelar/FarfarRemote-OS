package org.farfarremote;

import android.net.Uri;
import android.text.Html;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/** Small keyless online metadata lookup. Call from a background executor only. */
final class OnlineMetadataClient {
    static final class Result {
        final String description, source, url, title;
        Result(String description, String source, String url, String title) {
            this.description = description; this.source = source; this.url = url; this.title = title;
        }
        JSONObject toJson() {
            JSONObject value = new JSONObject();
            try { value.put("description", description); value.put("source", source); value.put("url", url); value.put("title", title); }
            catch (Exception ignored) { }
            return value;
        }
        static Result fromJson(JSONObject value) {
            if (value == null) return null;
            String description = value.optString("description", "");
            if (description.isEmpty()) return null;
            return new Result(description, value.optString("source", ""), value.optString("url", ""), value.optString("title", ""));
        }
    }

    private static final String USER_AGENT = "FarfarRemote/0.4 (GPL-3.0; media information)";
    private OnlineMetadataClient() { }

    static Result lookup(String query, boolean animeFirst, String mediaType) {
        if (query == null || query.trim().isEmpty()) return null;
        if (animeFirst) {
            Result anime = aniList(query);
            if (anime != null) return anime;
        }
        Result wiki = wikipedia(query, mediaType);
        if (wiki != null) return wiki;
        Result wikidata = wikidata(query);
        if (wikidata != null) return wikidata;
        // Anime feature films are often tagged as movies, so AniList is the final fallback.
        return animeFirst ? null : aniList(query);
    }

    private static Result aniList(String query) {
        HttpURLConnection connection = null;
        try {
            URL url = new URL("https://graphql.anilist.co");
            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(6500); connection.setReadTimeout(7500);
            connection.setRequestMethod("POST"); connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            connection.setRequestProperty("Accept", "application/json"); connection.setRequestProperty("User-Agent", USER_AGENT);
            JSONObject body = new JSONObject();
            body.put("query", "query ($search: String) { Page(perPage: 5) { media(search: $search, type: ANIME) { title { english romaji native } description(asHtml: false) siteUrl } } }");
            body.put("variables", new JSONObject().put("search", query));
            OutputStream output = connection.getOutputStream(); output.write(body.toString().getBytes("UTF-8")); output.close();
            JSONObject response = new JSONObject(readResponse(connection));
            JSONObject data = response.optJSONObject("data"); JSONObject page = data == null ? null : data.optJSONObject("Page");
            JSONArray media = page == null ? null : page.optJSONArray("media");
            JSONObject best = bestAniListMatch(media, query);
            if (best == null) return null;
            String description = cleanDescription(best.optString("description", ""));
            if (description.isEmpty() || !looksEnglish(description)) return null;
            JSONObject titles = best.optJSONObject("title");
            String title = titles == null ? query : first(titles.optString("english", ""), titles.optString("romaji", ""), titles.optString("native", ""), query);
            return new Result(description, "AniList", best.optString("siteUrl", "https://anilist.co/"), title);
        } catch (Exception ignored) { return null; }
        finally { if (connection != null) connection.disconnect(); }
    }

    private static JSONObject bestAniListMatch(JSONArray media, String query) {
        if (media == null) return null;
        JSONObject best = null; double bestScore = 0;
        for (int i = 0; i < media.length(); i++) {
            JSONObject candidate = media.optJSONObject(i); if (candidate == null) continue;
            JSONObject titles = candidate.optJSONObject("title"); if (titles == null) continue;
            double score = Math.max(titleScore(query, titles.optString("english", "")),
                    Math.max(titleScore(query, titles.optString("romaji", "")), titleScore(query, titles.optString("native", ""))));
            if (score > bestScore) { best = candidate; bestScore = score; }
        }
        return bestScore >= 0.72 ? best : null;
    }

    private static Result wikipedia(String query, String mediaType) {
        HttpURLConnection connection = null;
        try {
            String search = query;
            if ("movie".equalsIgnoreCase(mediaType)) search += " film";
            else if ("episode".equalsIgnoreCase(mediaType)) search += " television series";
            String address = "https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch="
                    + enc(search) + "&gsrlimit=5&prop=extracts%7Cinfo&exintro=1&explaintext=1&inprop=url&format=json&formatversion=2";
            connection = (HttpURLConnection) new URL(address).openConnection();
            connection.setConnectTimeout(6500); connection.setReadTimeout(7500);
            connection.setRequestProperty("Accept", "application/json"); connection.setRequestProperty("User-Agent", USER_AGENT);
            JSONObject response = new JSONObject(readResponse(connection));
            JSONObject results = response.optJSONObject("query"); JSONArray pages = results == null ? null : results.optJSONArray("pages");
            if (pages == null) return null;
            JSONObject best = null; double bestScore = 0;
            for (int i = 0; i < pages.length(); i++) {
                JSONObject candidate = pages.optJSONObject(i); if (candidate == null) continue;
                double score = titleScore(query, candidate.optString("title", ""));
                if (score > bestScore) { best = candidate; bestScore = score; }
            }
            if (best == null || bestScore < 0.72) return null;
            String description = cleanDescription(best.optString("extract", ""));
            if (description.isEmpty()) return null;
            String pageUrl = best.optString("fullurl", "");
            if (pageUrl.isEmpty()) pageUrl = "https://en.wikipedia.org/wiki/" + Uri.encode(best.optString("title", "").replace(' ', '_'));
            return new Result(description, "English Wikipedia (CC BY-SA 4.0)", pageUrl, best.optString("title", query));
        } catch (Exception ignored) { return null; }
        finally { if (connection != null) connection.disconnect(); }
    }

    private static Result wikidata(String query) {
        HttpURLConnection connection = null;
        try {
            String address = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + enc(query)
                    + "&language=en&uselang=en&type=item&limit=5&format=json";
            connection = (HttpURLConnection) new URL(address).openConnection();
            connection.setConnectTimeout(6500); connection.setReadTimeout(7500);
            connection.setRequestProperty("Accept", "application/json"); connection.setRequestProperty("User-Agent", USER_AGENT);
            JSONObject response = new JSONObject(readResponse(connection)); JSONArray results = response.optJSONArray("search");
            if (results == null) return null;
            JSONObject best = null; double bestScore = 0;
            for (int i = 0; i < results.length(); i++) {
                JSONObject candidate = results.optJSONObject(i); if (candidate == null) continue;
                double score = titleScore(query, candidate.optString("label", ""));
                if (score > bestScore) { best = candidate; bestScore = score; }
            }
            if (best == null || bestScore < 0.82) return null;
            String description = cleanDescription(best.optString("description", ""));
            if (description.isEmpty()) return null;
            String page = best.optString("concepturi", "");
            if (!page.startsWith("https://www.wikidata.org/")) page = "https://www.wikidata.org/wiki/" + best.optString("id", "");
            return new Result(description, "Wikidata (CC0)", page, best.optString("label", query));
        } catch (Exception ignored) { return null; }
        finally { if (connection != null) connection.disconnect(); }
    }

    private static String readResponse(HttpURLConnection connection) throws Exception {
        int code = connection.getResponseCode();
        InputStream input = code >= 200 && code < 300 ? connection.getInputStream() : connection.getErrorStream();
        if (input == null) throw new IllegalStateException("Metadata source returned HTTP " + code);
        ByteArrayOutputStream output = new ByteArrayOutputStream(); byte[] buffer = new byte[4096]; int count, total = 0;
        while ((count = input.read(buffer)) != -1) {
            total += count; if (total > 1024 * 1024) throw new IllegalStateException("Metadata response exceeded limit");
            output.write(buffer, 0, count);
        }
        input.close();
        if (code < 200 || code >= 300) throw new IllegalStateException("Metadata source returned HTTP " + code);
        return new String(output.toByteArray(), "UTF-8");
    }

    private static String cleanDescription(String raw) {
        if (raw == null) return "";
        String value = raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n");
        value = Html.fromHtml(value).toString().replaceAll("(?m)^\\s*[-*#]+\\s*", "").replaceAll("[*_~]", "").trim();
        return value.length() > 2200 ? value.substring(0, 2197).trim() + "…" : value;
    }

    private static boolean looksEnglish(String value) {
        for (int i = 0; i < value.length(); i++) {
            int c = value.codePointAt(i);
            if ((c >= 0x3040 && c <= 0x30ff) || (c >= 0x3400 && c <= 0x9fff)
                    || (c >= 0x0400 && c <= 0x052f) || (c >= 0x0600 && c <= 0x06ff)) return false;
            if (Character.isSupplementaryCodePoint(c)) i++;
        }
        return value.matches("(?is).*(\\b(the|a|an|and|or|of|to|in|is|are|with|for|when|from|on|his|her|their|this|that)\\b).*");
    }

    private static double titleScore(String query, String candidate) {
        String a = normalize(query), b = normalize(candidate);
        if (a.isEmpty() || b.isEmpty()) return 0;
        if (a.equals(b)) return 1;
        Set<String> left = words(a), right = words(b);
        if (left.isEmpty() || right.isEmpty()) return 0;
        int common = 0; for (String word : left) if (right.contains(word)) common++;
        return (2.0 * common) / (left.size() + right.size());
    }

    private static Set<String> words(String value) {
        HashSet<String> words = new HashSet<>();
        for (String word : value.split(" ")) if (word.length() > 1) words.add(word);
        return words;
    }

    private static String normalize(String value) {
        return value == null ? "" : value.toLowerCase(Locale.US).replaceAll("\\([^)]*\\)", " ")
                .replaceAll("[^a-z0-9]+", " ").trim().replaceAll("\\s+", " ");
    }

    private static String first(String... values) { for (String value : values) if (value != null && !value.trim().isEmpty()) return value.trim(); return ""; }
    private static String enc(String value) throws Exception { return URLEncoder.encode(value, "UTF-8"); }
}
