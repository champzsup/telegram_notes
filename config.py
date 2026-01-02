from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = "/app"
DATA_DIR = os.path.join(BASE_DIR, "data")

AUDIO_DIR = os.path.join(BASE_DIR, "audio")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
NOTES_DIR = os.path.join(BASE_DIR, "notes")

# === API / Secrets ===
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

# === Telegram session ===
TELEGRAM_SESSION_PATH = os.getenv(
    "TELEGRAM_SESSION_PATH",
    "/data/telegram.session"
)
