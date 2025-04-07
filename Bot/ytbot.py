from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import redis
import os
import uuid
from shared.redis_queue import enqueue_download

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube link!")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    ydl_opts = {'quiet': True, 'skip_download': True, 'force_generic_extractor': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get('title')
        thumb = info.get('thumbnail')
        formats = info.get('formats', [])

        keyboard = []
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('filesize') and f.get('height'):
                btn_text = f"{f['height']}p - {round(f['filesize'] / (1024*1024), 2)}MB"
                callback_data = f"{url}|{f['format_id']}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])

        await update.message.reply_photo(photo=thumb, caption=title,
            reply_markup=InlineKeyboardMarkup(keyboard[:10]))

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    url, format_id = data.split("|")
    task_id = str(uuid.uuid4())

    enqueue_download(task_id, {
        "user_id": query.from_user.id,
        "url": url,
        "format_id": format_id
    })

    await query.edit_message_caption(f"Task queued. ID: {task_id}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button_callback))

app.run_polling()