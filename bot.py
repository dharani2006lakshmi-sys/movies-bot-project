import os
import re
import zipfile
import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── CONFIG (set via environment variables) ───────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

if not BOT_TOKEN:
    logger.error("Missing BOT_TOKEN. Please set it as an environment variable or in a .env file.")
    exit(1)

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "spotify_bot"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def create_zip(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in src_dir.iterdir():
            if f.is_file() and f.suffix != ".zip":
                zf.write(f, f.name)

# ─── BOT HANDLERS ────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 *Spotify Playlist → ZIP Bot*\n\n"
        "Send me a Spotify playlist link and I'll download all songs "
        "as MP3s with thumbnails & metadata, then pack them into a ZIP.\n\n"
        "Usage:\n`/download https://open.spotify.com/playlist/...`\n\n"
        "⚠️ Large playlists take time — please be patient!",
        parse_mode="Markdown",
    )

async def download_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide a Spotify playlist URL.\n"
            "Example: `/download https://open.spotify.com/playlist/37i9dQ...`",
            parse_mode="Markdown",
        )
        return

    url = context.args[0]
    if "spotify.com" not in url:
        await update.message.reply_text("❌ Invalid Spotify URL.")
        return

    status_msg = await update.message.reply_text("🔍 Starting download using spotdl... This might take a few minutes depending on the playlist size.")

    # Work in a temp directory
    playlist_id = url.split('/')[-1].split('?')[0] # just an approximation for uniqueness
    work_dir = DOWNLOAD_DIR / playlist_id
    work_dir.mkdir(exist_ok=True, parents=True)

    try:
        # Run spotdl via subprocess
        cmd = [
            "python", "-m", "spotdl", url,
            "--format", "mp3",
            "--output", str(work_dir / "{list-position} - {title} - {artist}.{output-ext}")
        ]
        
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            cmd.extend([
                "--client-id", SPOTIFY_CLIENT_ID,
                "--client-secret", SPOTIFY_CLIENT_SECRET
            ])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Start a background task to update progress
        async def update_progress():
            last_count = -1
            while process.returncode is None:
                current_count = len(list(work_dir.glob("*.mp3")))
                if current_count != last_count:
                    last_count = current_count
                    try:
                        await status_msg.edit_text(f"⏳ Downloading... {current_count} songs downloaded so far.")
                    except Exception:
                        pass
                await asyncio.sleep(4)
                
        progress_task = asyncio.create_task(update_progress())
        
        stdout, stderr = await process.communicate()
        progress_task.cancel()
        
        if process.returncode != 0:
            logger.error(f"spotdl error: {stderr.decode()}")
            await status_msg.edit_text("❌ Failed to download playlist. Please ensure the URL is correct and public.")
            return

        # Create ZIP
        # We don't have the playlist name easily, so we'll just name it based on ID or "Spotify_Playlist"
        zip_name = f"Spotify_Playlist_{playlist_id}.zip"
        zip_path = DOWNLOAD_DIR / zip_name
        
        await status_msg.edit_text("📦 Packing ZIP…")
        create_zip(work_dir, zip_path)

        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

        if zip_size_mb > 50:
            await status_msg.edit_text(
                f"⚠️ ZIP is {zip_size_mb:.1f} MB — too large for Telegram (50 MB limit).\n"
                "Consider splitting the playlist into smaller parts."
            )
        else:
            await status_msg.edit_text(f"📦 Sending ZIP ({zip_size_mb:.1f} MB)…")
            with open(zip_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=zip_name,
                    caption="🎵 Here is your downloaded playlist!",
                )
            await status_msg.delete()

    except Exception as e:
        logger.error(f"Error processing playlist: {e}")
        await status_msg.edit_text(f"❌ An unexpected error occurred.")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)
        if 'zip_path' in locals() and zip_path.exists():
            zip_path.unlink(missing_ok=True)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-detect Spotify playlist URLs in plain messages."""
    text = update.message.text or ""
    if "spotify.com" in text:
        context.args = text.split()
        for word in text.split():
            if "spotify.com" in word:
                context.args = [word]
                break
        await download_playlist(update, context)
    else:
        await update.message.reply_text(
            "Send a Spotify playlist URL or use `/download <url>`",
            parse_mode="Markdown",
        )

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("help",     start))
    app.add_handler(CommandHandler("download", download_playlist))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    logger.info("Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
