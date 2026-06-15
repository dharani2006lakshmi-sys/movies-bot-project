import requests
import base64

client_id = "8f515e3789454157bc8cb9eb070ed0e2"
client_secret = "0f1d07c0cfbc483ba0a10df4863fba88"

try:
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=15,
    )
    print("Status:", resp.status_code)
    print("Result:", resp.text)
except Exception as e:
    print("Error:", e)
