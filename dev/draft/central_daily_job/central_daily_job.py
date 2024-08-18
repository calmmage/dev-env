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
from dotenv import load_dotenv
import os
load_dotenv()
import pyrogram

def get_pyrogram_client():
    import pyrogram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    # api_id = 12345
    # api_hash = "0123456789abcdef0123456789abcdef"

    app = pyrogram.Client("my_account")
    pyrogram_client = pyrogram.Client("calmmage-dev-env-bot", bot_token=bot_token)
    # app.run()
    return pyrogram_client


pyrogram_client = get_pyrogram_client()
def send_telegram_message_with_pyrogram(message: str):
    pyrogram_client.send_message(
        chat_id=os.getenv("DEV_ENV_NOTIFICATIONS_TELEGRAM_CHAT_ID"),
        text=message
    )

if __name__ == '__main__':
    # pyrogram_client.run()
    # text = "This is a test notification from calmmage dev env central daily job on a macbook"
    # send_telegram_message_with_pyrogram(text)
    import asyncio
    from pyrogram import Client

    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"


    async def main():
        async with Client("my_account", api_id, api_hash) as app:
            await app.send_message("me", "Greetings from **Pyrogram**!")


    asyncio.run(main())
    # pyrogram_client = pyrogram.Client("calmmage-dev-env-bot")
    # pyrogram_client.run()
