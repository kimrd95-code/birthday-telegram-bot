from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class BotContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        bot = data.get("bot")
        if bot:
            me = await bot.get_me()
            data["bot_username"] = me.username or ""
            data["bot_link"] = f"https://t.me/{me.username}" if me.username else ""
        else:
            data["bot_username"] = ""
            data["bot_link"] = ""
        return await handler(event, data)
