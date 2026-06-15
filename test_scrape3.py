import requests

url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
try:
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    data = response.json()
    print("IsAnonymous:", data.get("isAnonymous"))
    token = data.get("accessToken")
    print("Token found:", bool(token))
    
    if token:
        # Test fetching a playlist
        api_url = "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M"
        api_headers = {"Authorization": f"Bearer {token}", "User-Agent": headers["User-Agent"]}
        r = requests.get(api_url, headers=api_headers)
        print("API Status:", r.status_code)
        if r.status_code == 200:
            playlist_data = r.json()
            print("Playlist:", playlist_data.get('name'))
            print("Tracks:", playlist_data.get('tracks', {}).get('total'))
except Exception as e:
    print("Error:", e)
