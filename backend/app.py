from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import download_video_or_playlist, get_metadata, get_available_formats

app = Flask(__name__)
CORS(app)  # Allow all origins for now; you can restrict to frontend URL

# 🔍 SEARCH
@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q") or request.args.get("query")
    if not q:
        return jsonify({"error": "Missing search text"}), 400

    from yt_dlp import YoutubeDL
    opts = {"quiet": True, "ignoreerrors": True}
    with YoutubeDL(opts) as ydl:
        results = ydl.extract_info(f"ytsearch10:{q}", download=False)

    videos = []
    for entry in results.get("entries", []):
        if entry:
            videos.append({
                "title": entry.get("title"),
                "id": entry.get("id"),
                "thumbnail": entry.get("thumbnail"),
                "duration": entry.get("duration"),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
            })
    return jsonify(videos)


# ℹ️ METADATA
@app.route("/metadata", methods=["GET"])
def metadata_endpoint():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url"}), 400
    return jsonify(get_metadata(url))


# 🎞 FORMATS
@app.route("/formats", methods=["GET"])
def formats_endpoint():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url"}), 400
    return jsonify(get_available_formats(url))


# ⬇ DOWNLOAD ZIP
@app.route("/download", methods=["POST"])
def download_endpoint():
    data = request.json
    url = data.get("url")
    content_type = data.get("content_type", "Single Video")
    download_type = data.get("download_type", "video")
    quality = data.get("quality", "Best")
    zip_filename = data.get("zip_filename", "download.zip")

    if not url:
        return jsonify({"error": "URL required"}), 400

    zip_buffer = download_video_or_playlist(
        url=url,
        download_type=download_type,
        content_type=content_type,
        quality=quality,
        zip_output=True
    )

    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=zip_filename)


# ▶ WATCH ONLINE
@app.route("/watch-online", methods=["GET"])
def watch_online():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url"}), 400

    data = get_metadata(url)
    for fmt in data.get("formats", []):
        if fmt.get("acodec") != "none" and fmt.get("vcodec") != "none":
            if fmt.get("url"):
                return jsonify({"stream_url": fmt["url"]})

    return jsonify({"error": "No valid streaming link found"}), 404


@app.route("/")
def home():
    return {"message": "🔥 Flask backend running, Shyam the Emperor 🔥"}
