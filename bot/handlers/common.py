from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database import get_user_by_telegram, upsert_user_telegram
from bot.services.reminders import process_daily_reminders
from config import ADMIN_TELEGRAM_IDS
from bot.keyboards import start_registration_kb
from bot.texts import fmt, get

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(get("common.help"))


@router.message(Command("test_reminders"))
async def cmd_test_reminders(message: Message, bot_username: str) -> None:
    """Ручной запуск рассылки (только для ADMIN_TELEGRAM_IDS в .env)."""
    if message.from_user.id not in ADMIN_TELEGRAM_IDS:
        return
    await message.answer("Запускаю проверку напоминаний…")
    await process_daily_reminders(message.bot, bot_username)
    await message.answer("Готово. Проверьте личные сообщения у зарегистрированных пользователей.")


@router.message(Command("start"))
async def cmd_start(message: Message, bot_link: str = "") -> None:
    if message.chat.type != "private":
        link = bot_link or "https://t.me/"
        await message.answer(fmt("common.need_start", bot_link=link))
        return

    username = message.from_user.username if message.from_user else None
    await upsert_user_telegram(message.from_user.id, username)
    user = await get_user_by_telegram(message.from_user.id)

    if user and user.is_registered:
        from bot.context_builders import user_context
        from bot.handlers.profile import show_profile

        bot_user = message.bot
        me = await bot_user.get_me()
        await show_profile(message, user, me.username or "")
        return

    await message.answer(get("start.welcome"), reply_markup=start_registration_kb())
