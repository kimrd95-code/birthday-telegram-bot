from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.context_builders import user_context
from bot.database import get_user_by_telegram, save_registration, upsert_user_telegram
from bot.keyboards import start_registration_kb
from bot.states import Registration
from bot.texts import fmt, get
from bot.utils import parse_birth_date

router = Router()


@router.callback_query(F.data == "reg:start")
async def reg_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(Registration.first_name)
    await callback.message.answer(get("registration.ask_first_name"))


@router.message(Registration.first_name)
async def reg_first_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(get("registration.ask_first_name"))
        return
    await state.update_data(first_name=name)
    await state.set_state(Registration.last_name)
    await message.answer(fmt("registration.ask_last_name", first_name=name))


@router.message(Registration.last_name)
async def reg_last_name(message: Message, state: FSMContext) -> None:
    last = (message.text or "").strip()
    if len(last) < 2:
        await message.answer(get("registration.ask_last_name"))
        return
    await state.update_data(last_name=last)
    await state.set_state(Registration.birth_date)
    await message.answer(get("registration.ask_birth_date"))


@router.message(Registration.birth_date)
async def reg_birth(message: Message, state: FSMContext) -> None:
    parsed = parse_birth_date(message.text or "")
    if not parsed:
        await message.answer(get("registration.invalid_date"))
        return
    day, month = parsed
    await state.update_data(birth_day=day, birth_month=month)
    await state.set_state(Registration.team)
    await message.answer(get("registration.ask_team"))


@router.message(Registration.team)
async def reg_team(message: Message, state: FSMContext) -> None:
    team = (message.text or "").strip()
    if len(team) < 2:
        await message.answer(get("registration.ask_team"))
        return
    data = await state.get_data()
    username = message.from_user.username if message.from_user else None
    await upsert_user_telegram(message.from_user.id, username)
    user = await save_registration(
        message.from_user.id,
        data["first_name"],
        data["last_name"],
        data["birth_day"],
        data["birth_month"],
        team,
        username,
    )
    await state.clear()
    me = await message.bot.get_me()
    ctx = user_context(user, me.username or "")
    await message.answer(fmt("registration.complete", **ctx))

