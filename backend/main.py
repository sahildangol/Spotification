from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import yt_dlp

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_playlist(token, playlist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={playlist_name}&type=playlist&limit=1"
    result = get(url + query, headers=headers)
    if result.status_code != 200:
        print(f"Spotify API error: {result.status_code}")
        print(result.text)
        return None

    data = json.loads(result.content)
    playlists = data.get("playlists", {}).get("items", [])
    
    if not playlists:
        print("No playlists found.")
        return None

    return playlists[0]["id"]

def get_tracks_from_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    tracks = []
    for item in json_result:
        track = item["track"]
        if track:
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            tracks.append(f"{track_name} {artist_name}")
    return tracks

def search_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    result = get(url + query, headers=headers)

    if result.status_code != 200:
        print(f"Spotify API error: {result.status_code}")
        print(result.text)
        return None

    data = json.loads(result.content)
    artists = data.get("artists", {}).get("items", [])
    
    if not artists:
        print("No artists found.")
        return None

    return artists[0]["id"]

def get_top_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    if result.status_code != 200:
        print("Failed to get top tracks")
        return []

    data = json.loads(result.content)
    tracks = []
    for track in data.get("tracks", []):
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        tracks.append(f"{track_name} {artist_name}")
    return tracks

def display_tracks(tracks):
    print("\n Available Tracks:\n")
    for idx,track in enumerate(tracks):
        print(f"{idx+1}.{track}")

def get_user_selected_tracks(tracks):
    display_tracks(tracks)
    selection_main=input("\n Do you Want to download All Tracks(Y/N):")
  
    if selection_main=="Y":
        print("Downloading all Songs")
        return tracks
        
    try:
        selection=input("\n Enter the track numbers you want to download:")
        selected_indices=[int(i.strip())-1 for i in selection.split()]
        selected_tracks=[tracks[i] for i in selected_indices if 0<=i<len(tracks)]
        return selected_tracks
    except Exception as e:
        print("Invalid Selection")
        return[]

def download_tracks_as_mp3(track_list):
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    for idx, track in enumerate(track_list):
        print(f"\n{idx + 1}. Downloading: {track}")
        query = f"ytsearch1:{track} audio"

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': f'downloads/{track}.%(ext)s',
            'quiet': False,
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([query])
        except Exception as e:
            print(f"Failed to download {track}: {e}")

if __name__ == "__main__":
    token = get_token()
    search_term = input("Enter an artist name or playlist name: ").strip()

    # Try artist first
    artist_id = search_artist(token, search_term)
    if artist_id:
        print(f"Found artist: fetching top tracks...")
        all_tracks = get_top_tracks(token, artist_id)
    else:
        print("Not an artist. Trying as playlist...")
        playlist_id = search_for_playlist(token, search_term)
        if playlist_id:
            all_tracks = get_tracks_from_playlist(token, playlist_id)
        else:
            print("Could not find artist or playlist. Try again.")
            exit(1)

    selected_tracks = get_user_selected_tracks(all_tracks)

    if selected_tracks:
        download_tracks_as_mp3(selected_tracks)
    else:
        print("No tracks selected.")
      