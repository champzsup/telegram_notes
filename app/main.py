import os
import asyncio
import logging
from config import AUDIO_DIR, TRANSCRIPTS_DIR, NOTES_DIR

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


CHAT_ID = "-1002416274269"
TOPIC_TITLE = "Lecture Topic Name"
START_ID = 5233
END_ID = 5640


async def run_pipeline():
    try:
        print("=== STEP 1: Download Telegram audio ===")
        logger.info("Starting audio download from Telegram...")
        await download_audio_topic(
            chat_id=CHAT_ID,
            start_id=START_ID,
            end_id=END_ID,
            download_folder=AUDIO_DIR,
            logger=logger
        )
        
        
        print("=== STEP 2: Transcribe audio ===")
        logger.info("Starting transcription of audio files...")
        batch_transcribe(
            downloads_folder=AUDIO_DIR,
            transcripts_folder=TRANSCRIPTS_DIR,
            logger=logger
        )


        print("=== STEP 3: Summarize transcripts ===")
        logger.info("Starting Summarization")
        process_topic_summarization(
            topic_title=TOPIC_TITLE,
            transcripts_folder=TRANSCRIPTS_DIR,
            notes_folder=NOTES_DIR,
            logger=logger
        )


        print("=== STEP 4: Upload to Notion ===")
        logger.info("Uploading summarized notes to Notion....")
        upload_to_notion(TOPIC_TITLE, notes_folder=NOTES_DIR, logger=logger)

        logger.info("Pipeline completed successfully!")
        print("=== PIPELINE COMPLETE ===")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline())