from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.context_builders import initiator_display, user_context
from bot.database import (
    cancel_pending,
    create_pending,
    get_event_by_id,
    get_pending_by_event,
    get_user_by_id,
    get_user_by_telegram,
)
from bot.keyboards import cancel_initiator_kb, join_chat_kb
from bot.texts import fmt, get

router = Router()


@router.callback_query(F.data.startswith("chat:create:"))
async def on_create_chat(callback: CallbackQuery, bot_username: str) -> None:
    await callback.answer()
    event_id = int(callback.data.split(":")[2])
    event = await get_event_by_id(event_id)
    if not event:
        return

    initiator = await get_user_by_telegram(callback.from_user.id)
    if not initiator or not initiator.is_registered:
        await callback.message.answer(get("common.need_registration"))
        return

    birthday_user = await get_user_by_id(event.birthday_user_id)
    if not birthday_user:
        return

    if event.chat_id and event.invite_link:
        init = await get_user_by_id(event.initiator_user_id) if event.initiator_user_id else None
        ctx = user_context(birthday_user, bot_username)
        await callback.message.answer(
            fmt(
                "initiator.already_created",
                **ctx,
                initiator_username_display=initiator_display(init),
                invite_link=event.invite_link,
            ),
            reply_markup=join_chat_kb(event.invite_link),
        )
        return

    pending = await get_pending_by_event(event_id)
    if pending:
        if pending[0] == initiator.id:
            ctx = user_context(birthday_user, bot_username)
            await callback.message.answer(
                fmt("initiator.instructions", **ctx),
                reply_markup=cancel_initiator_kb(event_id),
            )
            return
        init = await get_user_by_id(pending[0])
        ctx = user_context(birthday_user, bot_username)
        await callback.message.answer(
            f"Сейчас чат создаёт {initiator_display(init)}. "
            "Если не получится — попробуйте позже или дождитесь напоминания."
        )
        return

    await create_pending(event_id, initiator.id)
    ctx = user_context(birthday_user, bot_username)
    await callback.message.answer(
        fmt("initiator.instructions", **ctx),
        reply_markup=cancel_initiator_kb(event_id),
    )


@router.callback_query(F.data.startswith("chat:cancel:"))
async def on_cancel_chat(callback: CallbackQuery) -> None:
    await callback.answer()
    event_id = int(callback.data.split(":")[2])
    pending = await get_pending_by_event(event_id)
    user = await get_user_by_telegram(callback.from_user.id)
    if not pending or not user or pending[0] != user.id:
        return
    await cancel_pending(event_id)
    await callback.message.answer(get("initiator.cancelled"))
