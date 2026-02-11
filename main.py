import os
import logging
import tempfile
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Missing TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Yo, I'm *Joss*! \n\n"
        "📥 Drop an Instagram link — I'll send:\n"
        "✅ HD photo\n"
        "🎥 HD video (with sound)\n"
        "🚀 Instantly — no limits!",
        parse_mode='Markdown'
    )

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "instagram.com" not in text:
        return await update.message.reply_text("⚠️ Please send a valid Instagram link")

    msg = await update.message.reply_text("⏳ Downloading...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'format': 'bv[height<=1080]+ba/b[height<=1080]/best',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file_path = ydl.prepare_filename(info)

            if file_path.endswith('.webm'):
                mp4_path = file_path.replace('.webm', '.mp4')
                os.rename(file_path, mp4_path)
                file_path = mp4_path

            is_video = info.get('duration', 0) > 0 or file_path.endswith(('.mp4', '.mkv'))
            if is_video:
                await msg.edit_text("📤 Sending video...")
                await update.message.reply_video(open(file_path, 'rb'), caption=f"🎥 {info.get('title', 'Video')}", supports_streaming=True)
            else:
                await msg.edit_text("📤 Sending photo...")
                await update.message.reply_photo(open(file_path, 'rb'), caption=f"📸 {info.get('title', 'Photo')}")

        await msg.edit_text("🎉 Done!")

    except Exception as e:
        await msg.edit_text(f"❌ {str(e)[:80]}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))
    app.run_polling()
