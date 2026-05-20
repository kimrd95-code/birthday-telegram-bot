import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "9"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()

# Telegram ID админов через запятую (для /test_reminders)
_admin = os.getenv("ADMIN_TELEGRAM_IDS", "").strip()
ADMIN_TELEGRAM_IDS = [
    int(x.strip()) for x in _admin.split(",") if x.strip().isdigit()
]

# На Render можно задать путь к БД (по умолчанию data/bot.db в папке проекта)
_db = os.getenv("DATABASE_PATH", "").strip()
DATABASE_PATH = Path(_db) if _db else BASE_DIR / "data" / "bot.db"
MESSAGES_PATH = BASE_DIR / "messages.ru.yaml"

INITIATOR_TIMEOUT_HOURS = 12

# Дни до ДР для напоминаний
DAYS_WEEK_BEFORE = 7
DAYS_NO_CHAT_REMINDERS = (6, 4, 2)  # через день после -7: -6, -4, -2
DAYS_NOT_JOINED = 2
