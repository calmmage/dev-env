"""
Idea of this file
- this is a central daily job that runs every day via launchd
- try to run a list of python / bash scripts: wrap with try / except, save trace if error
- save stats somewhere (I guess to file for now)
- send telegram notifications if something goes wrong
- once a week send weekly report to telegram


Scripts that I want:
- sync all repos:
- stage, commit and push progress
- pull all changes
----
- dev env run / housekeeping
-
"""
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

load_dotenv()

def get_telegram_bot():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()
    return application.bot

telegram_bot = get_telegram_bot()

async def send_telegram_message(message: str):
    chat_id = os.getenv("DEV_ENV_NOTIFICATIONS_TELEGRAM_CHAT_ID")
    await telegram_bot.send_message(chat_id=chat_id, text=message)

if __name__ == '__main__':
    # pyrogram_client.run()
    text = "This is a test notification from calmmage dev env central daily job on a macbook"
    import asyncio
    asyncio.run(send_telegram_message(text))
