from telethon import TelegramClient, events
from shared.redis_queue import dequeue_download
import yt_dlp
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def download_worker():
    while True:
        task = dequeue_download()
        if task:
            user_id = task["user_id"]
            url = task["url"]
            fmt = task["format_id"]

            ydl_opts = {
                'format': fmt,
                'outtmpl': f'downloads/{user_id}.%(ext)s',
                'noplaylist': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.download([url])

            # Send the file
            files = os.listdir("downloads")
            for f in files:
                await client.send_file(user_id, f"downloads/{f}")
                os.remove(f"downloads/{f}")
        await asyncio.sleep(5)

@client.on(events.NewMessage(pattern='/ping'))
async def handler(event):
    await event.reply("Userbot alive")

async def main():
    await client.start()
    await download_worker()

client.loop.run_until_complete(main())