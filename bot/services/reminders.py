import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from bot.context_builders import initiator_display, user_context
from bot.database import (
    User,
    clear_expired_pending,
    get_event_by_id,
    get_or_create_event,
    get_user_by_id,
    is_member_of_event,
    list_registered_users,
    mark_reminder_flag,
)
from bot.keyboards import create_chat_kb, join_chat_kb
from bot.texts import fmt
from bot.utils import (
    days_until_birthday,
    event_year_key,
    next_birthday,
    today,
)
from config import DAYS_NO_CHAT_REMINDERS, DAYS_NOT_JOINED, DAYS_WEEK_BEFORE

logger = logging.getLogger(__name__)

FLAG_BY_DAYS = {6: "reminder_6_sent", 4: "reminder_4_sent", 2: "reminder_2_sent"}
MSG_BY_DAYS = {
    6: "reminder.no_chat_day_minus_6",
    4: "reminder.no_chat_day_minus_4",
    2: "reminder.no_chat_day_minus_2",
}


async def _send_safe(bot: Bot, telegram_id: int, text: str, reply_markup=None) -> bool:
    try:
        await bot.send_message(telegram_id, text, reply_markup=reply_markup)
        return True
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        logger.warning("Cannot send to %s: %s", telegram_id, e)
        return False


async def broadcast_except(
    bot: Bot,
    users: list[User],
    exclude_user_id: int | None,
    text: str,
    reply_markup=None,
) -> int:
    sent = 0
    for u in users:
        if exclude_user_id and u.id == exclude_user_id:
            continue
        if await _send_safe(bot, u.telegram_id, text, reply_markup):
            sent += 1
    return sent


async def process_daily_reminders(bot: Bot, bot_username: str) -> None:
    await clear_expired_pending()
    ref = today()
    all_users = await list_registered_users()

    for birthday_user in all_users:
        if not birthday_user.birth_day or not birthday_user.birth_month:
            continue

        days_left = days_until_birthday(
            birthday_user.birth_day, birthday_user.birth_month, ref
        )
        bday = next_birthday(
            birthday_user.birth_day, birthday_user.birth_month, ref
        )
        yk = event_year_key(birthday_user.id, bday)
        event = await get_or_create_event(
            birthday_user.id, bday.isoformat(), yk
        )
        ctx = user_context(birthday_user, bot_username)

        # День рождения — поздравление имениннику
        if days_left == 0 and not event.birthday_congrats_sent:
            from bot.utils import congrats_variant

            path = congrats_variant(birthday_user.id, bday.year)
            text = fmt(path, **ctx)
            if await _send_safe(bot, birthday_user.telegram_id, text):
                await mark_reminder_flag(event.id, "birthday_congrats_sent")
            continue

        if days_left == DAYS_WEEK_BEFORE and not event.reminder_7_sent:
            text = fmt("reminder.week_before", **ctx)
            kb = create_chat_kb(event.id) if not event.chat_id else None
            if event.chat_id and event.invite_link:
                init = await get_user_by_id(event.initiator_user_id) if event.initiator_user_id else None
                text = fmt(
                    "reminder.chat_exists",
                    **ctx,
                    initiator_username_display=initiator_display(init),
                    invite_link=event.invite_link,
                )
                kb = join_chat_kb(event.invite_link)
            await broadcast_except(
                bot, all_users, birthday_user.id, text, kb
            )
            await mark_reminder_flag(event.id, "reminder_7_sent")
            continue

        if days_left in DAYS_NO_CHAT_REMINDERS and not event.chat_id:
            flag = FLAG_BY_DAYS[days_left]
            if getattr(event, flag):
                continue
            msg_key = MSG_BY_DAYS[days_left]
            text = fmt(msg_key, **ctx)
            kb = create_chat_kb(event.id)
            await broadcast_except(
                bot, all_users, birthday_user.id, text, kb
            )
            await mark_reminder_flag(event.id, flag)
            continue

        if days_left == DAYS_NOT_JOINED and event.chat_id and event.invite_link:
            if not event.not_joined_sent:
                init = await get_user_by_id(event.initiator_user_id) if event.initiator_user_id else None
                text = fmt(
                    "reminder.not_joined",
                    **ctx,
                    initiator_username_display=initiator_display(init),
                    invite_link=event.invite_link,
                )
                kb = join_chat_kb(event.invite_link)
                for u in all_users:
                    if u.id == birthday_user.id:
                        continue
                    if await is_member_of_event(event.id, u.id):
                        continue
                    await _send_safe(bot, u.telegram_id, text, kb)
                await mark_reminder_flag(event.id, "not_joined_sent")


async def send_chat_link_broadcast(
    bot: Bot,
    event_id: int,
    bot_username: str,
) -> int:
    event = await get_event_by_id(event_id)
    if not event or not event.invite_link:
        return 0
    birthday_user = await get_user_by_id(event.birthday_user_id)
    initiator = await get_user_by_id(event.initiator_user_id) if event.initiator_user_id else None
    if not birthday_user:
        return 0
    ctx = user_context(birthday_user, bot_username)
    text = fmt(
        "broadcast.chat_link",
        **ctx,
        initiator_username_display=initiator_display(initiator),
        invite_link=event.invite_link,
    )
    kb = join_chat_kb(event.invite_link)
    all_users = await list_registered_users()
    return await broadcast_except(
        bot, all_users, birthday_user.id, text, kb
    )
