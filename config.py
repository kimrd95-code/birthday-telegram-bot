import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "9"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()

_admin = os.getenv("ADMIN_TELEGRAM_IDS", "").strip()
ADMIN_TELEGRAM_IDS = [
    int(x.strip()) for x in _admin.split(",") if x.strip().isdigit()
]

_db = os.getenv("DATABASE_PATH", "").strip()
DATABASE_PATH = Path(_db) if _db else BASE_DIR / "data" / "bot.db"
MESSAGES_PATH = BASE_DIR / "messages.ru.yaml"

INITIATOR_TIMEOUT_HOURS = 12
DAYS_WEEK_BEFORE = 7
DAYS_NO_CHAT_REMINDERS = (6, 4, 2)
DAYS_NOT_JOINED = 2

# Render Free = Web Service (не Worker). Webhook + внешний cron.
PORT = int(os.getenv("PORT", "10000"))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
WEBHOOK_BASE = os.getenv("WEBHOOK_URL", "").strip().rstrip("/") or RENDER_URL
_use = os.getenv("USE_WEBHOOK", "").strip().lower()
USE_WEBHOOK = _use in ("1", "true", "yes") or bool(RENDER_URL and os.getenv("RENDER"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
CRON_SECRET = os.getenv("CRON_SECRET", "").strip()
