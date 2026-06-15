import requests
import re
import json

url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)

# Find the access token
token_match = re.search(r'"accessToken":"(.*?)"', response.text)
if token_match:
    token = token_match.group(1)
    print("Found token!", len(token))
    
    # Try fetching playlist with this token
    api_url = "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M"
    api_headers = {"Authorization": f"Bearer {token}", "User-Agent": headers["User-Agent"]}
    r = requests.get(api_url, headers=api_headers)
    print("API Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Playlist Name:", data.get('name'))
        print("Total Tracks:", data.get('tracks', {}).get('total'))
else:
    print("Token not found.")

# Let's also save the HTML just to inspect if token wasn't found
with open("spotify_test.html", "w", encoding="utf-8") as f:
    f.write(response.text)
