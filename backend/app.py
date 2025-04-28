from flask import Flask, request, jsonify
from flask_cors import CORS
from main import get_token, search_artist, get_top_tracks, search_for_playlist, get_tracks_from_playlist, download_tracks_as_mp3

app = Flask(__name__)
CORS(app)

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    token = get_token()

    artist_id = search_artist(token, query)
    if artist_id:
        tracks = get_top_tracks(token, artist_id)
    else:
        playlist_id = search_for_playlist(token, query)
        if playlist_id:
            tracks = get_tracks_from_playlist(token, playlist_id)
        else:
            return jsonify({"error": "No artist or playlist found"}), 404

    return jsonify({"tracks": tracks})

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    tracks = data.get("tracks", [])
    download_tracks_as_mp3(tracks)
    return jsonify({"status": "Download started"})

if __name__ == "__main__":
    app.run(debug=True)
