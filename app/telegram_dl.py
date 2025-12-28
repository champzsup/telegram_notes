import os
import logging


logger = logging.getLogger(__name__)

def is_audio_message(message):
    if message.voice:
        return True

    if message.audio:
        return True

    if message.document:
        mime = message.document.mime_type or ""
        return mime.startswith("audio/")

    return False

def already_downloaded(message_id, audio_dir):
    return any(
        fname.startswith(str(message_id))
        for fname in os.listdir(audio_dir)
    )

def rename_to_message_id(path, message_id):
    ext = os.path.splitext(path)[1]
    new_path = os.path.join(
        os.path.dirname(path),
        f"{message_id}{ext}"
    )
    os.rename(path, new_path)
    return new_path

async def download_audio_topic(client, chat_id, start_id, end_id, download_folder, logger):
    logger.info(f"Client connected? {client.is_connected()}")
    os.makedirs(download_folder, exist_ok=True)

    async for message in client.iter_messages(
        chat_id,
        min_id=start_id,
        max_id=end_id,
        reverse=True
    ):
        if not is_audio_message(message):
            continue

        if already_downloaded(message.id, download_folder):
            logger.info(f"Already exists: {message.id}")
            continue
        
        logger.info("Starting Telegram Audio Download ...")
        downloaded_path = await message.download_media(file=download_folder)
        if downloaded_path:
            final_path = rename_to_message_id(downloaded_path, message.id)
            logger.info(f"Downloaded: {final_path}")

    logger.info("All audio files downloaded")
