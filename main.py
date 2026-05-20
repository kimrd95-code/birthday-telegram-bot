import asyncio
import logging
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from bot.database import init_db
from bot.handlers import setup_routers
from bot.middleware import BotContextMiddleware
from bot.services.reminders import process_daily_reminders
from config import (
    BOT_TOKEN,
    CRON_SECRET,
    PORT,
    REMINDER_HOUR,
    TIMEZONE,
    USE_WEBHOOK,
    WEBHOOK_BASE,
    WEBHOOK_SECRET,
)

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


def build_bot_and_dp() -> tuple[Bot, Dispatcher]:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(BotContextMiddleware())
    dp.include_router(setup_routers())
    return bot, dp


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
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
    logger.info("Mode: polling. Scheduler daily at %s:00 (%s)", REMINDER_HOUR, TIMEZONE)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


async def run_webhook_server(bot: Bot, dp: Dispatcher) -> None:
    if not WEBHOOK_BASE:
        logger.error("USE_WEBHOOK без WEBHOOK_URL / RENDER_EXTERNAL_URL")
        sys.exit(1)
    if not CRON_SECRET:
        logger.error("Задайте CRON_SECRET в Environment Variables (любая длинная случайная строка)")
        sys.exit(1)

    webhook_url = f"{WEBHOOK_BASE}/webhook"
    logger.info("Mode: webhook. URL: %s", webhook_url)

    async def on_startup(_app: web.Application) -> None:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET or None,
            allowed_updates=dp.resolve_used_update_types(),
        )
        logger.info("Telegram webhook set")

    async def on_shutdown(_app: web.Application) -> None:
        await bot.session.close()

    async def health(_request: web.Request) -> web.Response:
        return web.Response(text="ok")

    async def cron_daily(request: web.Request) -> web.Response:
        if request.rel_url.query.get("key") != CRON_SECRET:
            return web.Response(status=403, text="forbidden")
        await run_daily_job(bot)
        return web.Response(text="ok")

    app = web.Application()
    app["bot"] = bot
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET or None,
    ).register(app, path="/webhook")

    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    app.router.add_get("/cron/daily", cron_daily)

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info("HTTP server on port %s", PORT)
    await asyncio.Event().wait()


async def main() -> None:
    if not BOT_TOKEN or "BOT_TOKEN=" in BOT_TOKEN or BOT_TOKEN.startswith("123456789"):
        logger.error(
            "Укажите BOT_TOKEN: локально в .env, на Render — в Environment Variables."
        )
        sys.exit(1)

    await init_db()
    bot, dp = build_bot_and_dp()

    if USE_WEBHOOK:
        await run_webhook_server(bot, dp)
    else:
        await run_polling(bot, dp)


if __name__ == "__main__":
    asyncio.run(main())
