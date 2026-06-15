# Spotify Playlist → ZIP Telegram Bot

## What it does
User sends a Spotify playlist link → Bot:
1. Fetches all track info via Spotify API
2. Searches YouTube for each track using `yt-dlp`
3. Downloads as MP3 with embedded thumbnail & metadata
4. Downloads playlist cover image
5. Writes a `playlist_metadata.json` file
6. Zips everything into `PlaylistName.zip`
7. Sends the ZIP back on Telegram

---

## Setup

### 1. Install system dependencies
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg

# Install yt-dlp (latest)
pip install yt-dlp --upgrade
```

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

### 3. Get your credentials

#### Telegram Bot Token
1. Open Telegram → search **@BotFather**
2. Send `/newbot` → follow instructions
3. Copy the token

#### Spotify API Credentials
1. Go to https://developer.spotify.com/dashboard
2. Click **Create App**
3. Copy **Client ID** and **Client Secret**

### 4. Set environment variables
```bash
export BOT_TOKEN="your_telegram_bot_token"
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

Or create a `.env` file and use `python-dotenv`:
```
BOT_TOKEN=your_telegram_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### 5. Run the bot
```bash
python bot.py
```

---

## Usage
- Send `/start` or `/help` — shows instructions
- Send `/download https://open.spotify.com/playlist/...`
- Or just paste the Spotify playlist URL directly

---

## ZIP Contents
```
PlaylistName.zip
├── cover.jpg                    ← Playlist cover image
├── playlist_metadata.json       ← Full metadata (title, artist, album, year...)
├── Artist - Track 1.mp3         ← MP3 with embedded thumbnail + ID3 tags
├── Artist - Track 2.mp3
└── ...
```

---

## Notes
- Telegram has a **50 MB file size limit** — large playlists may exceed this
- For big playlists (50+ songs), consider splitting into parts
- `yt-dlp` matches songs by searching YouTube — accuracy is ~90%
- Tracks longer than 10 minutes are skipped (configurable in bot.py)
- Works on any platform with Python 3.11+ and ffmpeg

---

## Troubleshooting
| Issue | Fix |
|-------|-----|
| `yt-dlp not found` | Run `pip install yt-dlp` |
| `ffmpeg not found` | Install ffmpeg from https://ffmpeg.org |
| `401 Unauthorized` from Spotify | Check your Client ID/Secret |
| ZIP too large | Playlist has too many/large songs; split playlist |
