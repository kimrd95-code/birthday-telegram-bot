from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.context_builders import user_context
from bot.database import get_user_by_telegram, save_registration, upsert_user_telegram
from bot.keyboards import start_registration_kb
from bot.registration_flow import (
    cancel_registration,
    go_back,
    prompt_birth_date,
    prompt_first_name,
    prompt_last_name,
    prompt_team,
    show_welcome,
)
from bot.states import Registration
from bot.texts import fmt, get
from bot.utils import parse_birth_date

router = Router()


@router.callback_query(F.data == "reg:start")
async def reg_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(Registration.first_name)
    await prompt_first_name(callback.message)


@router.callback_query(F.data == "reg:cancel", StateFilter(Registration))
async def reg_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await cancel_registration(callback.message, state)


@router.callback_query(F.data == "reg:back", StateFilter(Registration))
async def reg_back(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await go_back(callback.message, state)


@router.callback_query(F.data.startswith("reg:month:"), StateFilter(Registration.birth_date))
async def reg_pick_month(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    month = int(callback.data.split(":")[-1])
    if not 1 <= month <= 12:
        return
    await state.update_data(pending_calendar_month=month)
    await prompt_birth_date(callback.message, state, pending_month=month)


@router.callback_query(F.data.startswith("reg:day:"), StateFilter(Registration.birth_date))
async def reg_pick_day(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    month = data.get("pending_calendar_month")
    if not month:
        await prompt_birth_date(callback.message, state)
        return
    day = int(callback.data.split(":")[-1])
    await state.update_data(birth_day=day, birth_month=month, pending_calendar_month=None)
    await state.set_state(Registration.team)
    await prompt_team(callback.message)


@router.message(Registration.first_name)
async def reg_first_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer(get("registration.invalid_name"))
        await prompt_first_name(message)
        return
    await state.update_data(first_name=name)
    await state.set_state(Registration.last_name)
    await prompt_last_name(message, first_name=name)


@router.message(Registration.last_name)
async def reg_last_name(message: Message, state: FSMContext) -> None:
    last = (message.text or "").strip()
    if len(last) < 2:
        await message.answer(get("registration.invalid_name"))
        data = await state.get_data()
        await prompt_last_name(message, first_name=data.get("first_name", ""))
        return
    await state.update_data(last_name=last)
    await state.set_state(Registration.birth_date)
    await prompt_birth_date(message, state)


@router.message(Registration.birth_date)
async def reg_birth(message: Message, state: FSMContext) -> None:
    parsed = parse_birth_date(message.text or "")
    if not parsed:
        await message.answer(get("registration.invalid_date"))
        data = await state.get_data()
        pending = data.get("pending_calendar_month")
        await prompt_birth_date(message, state, pending_month=pending)
        return
    day, month = parsed
    await state.update_data(birth_day=day, birth_month=month, pending_calendar_month=None)
    await state.set_state(Registration.team)
    await prompt_team(message)


@router.message(Registration.team)
async def reg_team(message: Message, state: FSMContext) -> None:
    team = (message.text or "").strip()
    if len(team) < 2:
        await message.answer(get("registration.invalid_team"))
        await prompt_team(message)
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
