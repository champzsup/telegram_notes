import whisper
import os
import logging

logger = logging.getLogger(__name__)

def load_model():
    logger.info("Loading Whisper model (small)...")
    print("Loading Whisper model (small)...")
    return whisper.load_model("small")

def transcribe_ogg(model, file_path):
    logger.info(f"Transcribing {file_path} ...")
    print(f"Transcribing {file_path} ...")

    result = model.transcribe(
        file_path,
        language="en",
        fp16=False,
        temperature=0.0,
        compression_ratio_threshold=2.4,
        logprob_threshold=-1.0,
        no_speech_threshold=0.6,
        condition_on_previous_text=False
    )

    return result["text"].strip()

def save_transcript(text, audio_file_path, transcripts_folder):
    os.makedirs(transcripts_folder, exist_ok=True)
    base = os.path.splitext(os.path.basename(audio_file_path))[0]
    file_name = os.path.basename(audio_file_path).replace(".ogg", ".txt")
    save_path = os.path.join(transcripts_folder, f"{base}.txt")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    logger.info(f"Saved transcript → {save_path}")
    print(f"Saved transcript → {save_path}")

def batch_transcribe(downloads_folder, transcripts_folder, logger):
    model = load_model()

    for file in sorted(os.listdir(downloads_folder)):
        if not file.lower().endswith((".ogg", ".opus", ".aac", ".mp3", ".wav", "oga")):
            continue

        audio_path = os.path.join(downloads_folder, file)
        txt_path = os.path.join(
            transcripts_folder,
            os.path.splitext(file)[0] + ".txt"
        )

        if os.path.exists(txt_path):
            continue

        try:
            text = transcribe_ogg(model, audio_path)
            save_transcript(text, audio_path, transcripts_folder)
        except Exception as e: 
            logger.info(f"Failed to transcribe {file}: {e}")
            print(f"Failed to transcribe {file}: {e}")
