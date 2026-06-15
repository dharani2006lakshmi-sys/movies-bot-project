import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

# Get access token
auth_response = requests.post(
    "https://accounts.spotify.com/api/token",
    data={"grant_type": "client_credentials"},
    auth=(CLIENT_ID, CLIENT_SECRET)
)
token = auth_response.json().get("access_token")

# Get playlist
playlist_id = "2aymSy2CuAkozUSCwOX0GN"
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)

if r.status_code == 200:
    data = r.json()
    tracks = data["tracks"]["items"]
    print(f"Found {len(tracks)} tracks!")
    for t in tracks[:3]:
        track = t["track"]
        name = track["name"]
        artist = track["artists"][0]["name"]
        print(f"- {name} by {artist}")
else:
    print("Failed!", r.status_code, r.text)
