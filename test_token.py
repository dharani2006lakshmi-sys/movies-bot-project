import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
r = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player", headers=headers)
print(r.status_code)
print(r.text[:200])
