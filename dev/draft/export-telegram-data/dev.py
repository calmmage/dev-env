# let's login 
# bonus - can we install trcrypto? no, don't care about speed
from pyrogram import Client
from loguru import logger
from dotenv import load_dotenv
import os
import asyncio
from pathlib import Path
from tqdm import tqdm
# Load environment variables
load_dotenv()

# Configure logger
logger.add("pyrogram_example.log", rotation="1 MB")

target_dir_path = Path("/Users/petrlavrov/work/projects/dev-env/dev/draft/export-telegram-data") / "data"
target_dir_path.mkdir(parents=True, exist_ok=True)

# https://t.me/c/1717327731/977/978
# club 146
target_chat_id = -1001717327731

# thread
thread_id = 977

# Pyrogram client setup
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
async def main():
    async with Client("my_account", api_id, api_hash) as app:
        try:   

            # step 1: load all messages

            # step 2: filter out messages not with thread_id

            # step 3: dump to text
            for message_id in tqdm(range(978, 10000)):
            
                data = await app.get_messages(target_chat_id, message_id)

                # if data.message_thread_id != thread_id:
                #     continue

                    
                target_path = target_dir_path / f"{message_id}.json"
                
                target_path.write_text(str(data))
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
# # Run the main function
# await main()
