from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.context_builders import user_context
from bot.database import (
    get_user_by_telegram,
    update_user_field,
)
from bot.keyboards import profile_kb
from bot.states import ProfileEdit
from bot.texts import fmt, get
from bot.utils import parse_birth_date

router = Router()


async def show_profile(message: Message, user, bot_username: str) -> None:
    ctx = user_context(user, bot_username)
    await message.answer(fmt("profile.view", **ctx), reply_markup=profile_kb())


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await get_user_by_telegram(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(get("common.need_registration"))
        return
    me = await message.bot.get_me()
    await show_profile(message, user, me.username or "")


@router.callback_query(F.data.startswith("prof:"))
async def profile_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    field = callback.data.split(":")[1]
    prompts = {
        "first_name": get("registration.ask_first_name"),
        "last_name": get("registration.ask_last_name"),
        "birth_date": get("registration.ask_birth_date"),
        "team": get("registration.ask_team"),
    }
    await state.set_state(ProfileEdit.value)
    await state.update_data(edit_field=field)
    await callback.message.answer(prompts[field])


@router.message(ProfileEdit.value)
async def profile_edit_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data.get("edit_field")
    user = await get_user_by_telegram(message.from_user.id)
    if not user:
        await state.clear()
        return

    text = (message.text or "").strip()
    if field == "first_name" and len(text) >= 2:
        await update_user_field(user.id, "first_name", text)
    elif field == "last_name" and len(text) >= 2:
        await update_user_field(user.id, "last_name", text)
    elif field == "team" and len(text) >= 2:
        await update_user_field(user.id, "team", text)
    elif field == "birth_date":
        parsed = parse_birth_date(text)
        if not parsed:
            await message.answer(get("registration.invalid_date"))
            return
        day, month = parsed
        await update_user_field(user.id, "birth_day", day)
        await update_user_field(user.id, "birth_month", month)
    else:
        await message.answer(get("registration.ask_first_name"))
        return

    await state.clear()
    user = await get_user_by_telegram(message.from_user.id)
    await message.answer(get("profile.saved"))
    me = await message.bot.get_me()
    await show_profile(message, user, me.username or "")
