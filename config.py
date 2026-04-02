import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", 4))

    # ✅ NEW (Support)
    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "")
    SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")


def validate():
    if not Config.API_ID or not Config.API_HASH or not Config.BOT_TOKEN:
        raise ValueError("❌ Missing environment variables!")