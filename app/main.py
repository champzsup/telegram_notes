import asyncio
import logging
from telethon import TelegramClient
from config import AUDIO_DIR, TRANSCRIPTS_DIR, NOTES_DIR
from config import TELEGRAM_SESSION_PATH, API_ID, API_HASH, PHONE_NUMBER

from app.telegram_dl import download_audio_topic
from app.summarize import process_topic_summarization
from app.notion_upload import upload_to_notion
from app.transcribe import batch_transcribe

# === Configure logging centrally ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

client = TelegramClient(TELEGRAM_SESSION_PATH, API_ID, API_HASH)

CHAT_ID = -1002416274269
TOPIC_TITLE = "Cardio-vascular System"
START_ID = 5746
END_ID = 6012


async def run_pipeline():
    try:
        async with client:
            print("Logged in!")

            logger.info("=== STEP 1: Download Telegram audio ===")
            await download_audio_topic(client,
                chat_id=CHAT_ID,
                start_id=START_ID,
                end_id=END_ID,
                download_folder=AUDIO_DIR,
                logger=logger
            )
                
            logger.info("=== STEP 2: Transcribe audio ===")
            batch_transcribe(
                downloads_folder=AUDIO_DIR,
                transcripts_folder=TRANSCRIPTS_DIR,
                logger=logger
            )


            logger.info("=== STEP 3: Summarize transcripts ===")
            process_topic_summarization(
                topic_title=TOPIC_TITLE,
                transcripts_folder=TRANSCRIPTS_DIR,
                notes_folder=NOTES_DIR,
                logger=logger
            )


            logger.info("=== STEP 4: Upload to Notion ===")
            upload_to_notion(TOPIC_TITLE, notes_folder=NOTES_DIR, logger=logger)

            logger.info("=== PIPELINE COMPLETE ===")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline()) 