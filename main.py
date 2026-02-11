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
    await update.message.reply_text("📸 Joss Instagram Downloader — send a link!", parse_mode='Markdown')

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "instagram.com" not in text:
        return await update.message.reply_text("⚠️ Send Instagram link")

    msg = await update.message.reply_text("⏳...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {'outtmpl': f'{tmpdir}/%(id)s.%(ext)s', 'quiet': True, 'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                p = ydl.prepare_filename(info)
            if p.endswith('.webm'):
                os.rename(p, p.replace('.webm', '.mp4'))
                p = p.replace('.webm', '.mp4')
            if info.get('duration', 0) > 0:
                await msg.edit_text("🎥")
                await update.message.reply_video(open(p, 'rb'))
            else:
                await msg.edit_text("📸")
                await update.message.reply_photo(open(p, 'rb'))
        await msg.edit_text("✅ Done")
    except Exception as e:
        await msg.edit_text(f"❌ {str(e)[:50]}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))
    app.run_polling()