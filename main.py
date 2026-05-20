import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from bot.database import init_db
from bot.handlers import setup_routers
from bot.middleware import BotContextMiddleware
from bot.services.reminders import process_daily_reminders
from config import BOT_TOKEN, REMINDER_HOUR, TIMEZONE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run_daily_job(bot: Bot) -> None:
    me = await bot.get_me()
    username = me.username or ""
    logger.info("Running daily reminders...")
    await process_daily_reminders(bot, username)
    logger.info("Daily reminders done.")


async def main() -> None:
    if not BOT_TOKEN or "BOT_TOKEN=" in BOT_TOKEN or BOT_TOKEN.startswith("123456789"):
        logger.error(
            "Укажите BOT_TOKEN: локально в .env, на Render — в Environment Variables. "
            "Токен: @BotFather"
        )
        sys.exit(1)

    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(BotContextMiddleware())
    dp.include_router(setup_routers())

    tz = ZoneInfo(TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        run_daily_job,
        CronTrigger(hour=REMINDER_HOUR, minute=0, timezone=tz),
        args=[bot],
        id="daily_reminders",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler: daily at %s:00 (%s). Bot starting...",
        REMINDER_HOUR,
        TIMEZONE,
    )

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
