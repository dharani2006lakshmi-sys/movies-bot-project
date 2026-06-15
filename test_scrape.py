import requests
import json
from bs4 import BeautifulSoup
import re

url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

soup = BeautifulSoup(response.text, 'html.parser')
for script in soup.find_all('script'):
    if script.string and 'Spotify.Entity' in script.string:
        print("Found Spotify.Entity!")
        # We can extract data from this
        break
    if script.string and 'initial-state' in script.get('id', ''):
        print("Found initial-state!")

# Let's try to just use a simple regex to find tracks
matches = re.findall(r'"name":"([^"]+)","type":"track"', response.text)
print("Tracks found via regex:", len(matches))
if matches:
    print(matches[:5])
