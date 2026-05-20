from aiogram import F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, Message

from bot.context_builders import user_context
from bot.database import (
    find_event_by_chat_id,
    get_event_by_id,
    get_pending_by_initiator,
    get_user_by_id,
    get_user_by_telegram,
    record_chat_member,
    set_event_chat,
)
from bot.services.reminders import send_chat_link_broadcast
from bot.texts import fmt, get

router = Router()


@router.message(Command("done"))
async def cmd_done(message: Message, bot_username: str) -> None:
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("Команда /done работает только в группе, которую вы создали для поздравления.")
        return

    tg_user = message.from_user
    user = await get_user_by_telegram(tg_user.id)
    if not user:
        await message.answer(get("common.need_registration"))
        return

    event_id = await get_pending_by_initiator(user.id)
    if not event_id:
        await message.answer(get("initiator.no_pending"))
        return

    from bot.context_builders import initiator_display
    from bot.database import get_pending_by_event

    pend = await get_pending_by_event(event_id)
    if not pend or pend[0] != user.id:
        await message.answer(
            fmt(
                "initiator.wrong_user",
                initiator_username_display=initiator_display(
                    await get_user_by_id(pend[0]) if pend else None
                ),
            )
        )
        return

    event = await get_event_by_id(event_id)
    if not event:
        await message.answer(get("initiator.no_pending"))
        return

    if event.chat_id:
        await message.answer("Чат для этого дня рождения уже привязан.")
        return

    try:
        link = await message.bot.create_chat_invite_link(
            message.chat.id,
            name=f"bd_{event_id}",
        )
    except Exception:
        await message.answer(
            fmt("initiator.no_admin_rights", bot_username=bot_username)
        )
        return

    await set_event_chat(event_id, message.chat.id, link.invite_link, user.id)

    birthday_user = await get_user_by_id(event.birthday_user_id)
    ctx = user_context(birthday_user, bot_username)
    await message.answer(fmt("initiator.success", **ctx, invite_link=link.invite_link))

    await send_chat_link_broadcast(message.bot, event_id, bot_username)


@router.chat_member()
async def on_chat_member(update: ChatMemberUpdated) -> None:
    if update.new_chat_member.status not in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    ):
        return

    event = await find_event_by_chat_id(update.chat.id)
    if not event:
        return

    tg_id = update.new_chat_member.user.id
    user = await get_user_by_telegram(tg_id)
    if user:
        await record_chat_member(event.id, user.id)
