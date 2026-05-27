"""Подсказки и клавиатуры шагов регистрации."""

from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import birth_days_kb, birth_months_kb, registration_nav_kb
from bot.states import Registration
from bot.texts import fmt, get

REGISTRATION_STEPS = 4


def _progress(step: int) -> str:
    return fmt("registration.progress", step=step, total=REGISTRATION_STEPS)


async def show_welcome(message: Message) -> None:
    from bot.keyboards import start_registration_kb

    await message.answer(get("start.welcome"), reply_markup=start_registration_kb())


async def prompt_first_name(message: Message) -> None:
    text = f"{_progress(1)}\n\n{get('registration.ask_first_name')}"
    await message.answer(text, reply_markup=registration_nav_kb(step=1))


async def prompt_last_name(message: Message, *, first_name: str) -> None:
    text = f"{_progress(2)}\n\n{fmt('registration.ask_last_name', first_name=first_name)}"
    await message.answer(text, reply_markup=registration_nav_kb(step=2))


async def prompt_birth_date(
    message: Message,
    state: FSMContext,
    *,
    pending_month: int | None = None,
) -> None:
    if pending_month:
        month_name = get(f"registration.month_{pending_month}")
        text = (
            f"{_progress(3)}\n\n"
            f"{fmt('registration.ask_birth_pick_day', month_name=month_name)}"
        )
        await message.answer(
            text,
            reply_markup=birth_days_kb(pending_month, show_back=True),
        )
        return

    await state.update_data(pending_calendar_month=None)
    text = f"{_progress(3)}\n\n{get('registration.ask_birth_date')}"
    await message.answer(
        text,
        reply_markup=birth_months_kb(show_back=True),
    )


async def prompt_team(message: Message) -> None:
    text = f"{_progress(4)}\n\n{get('registration.ask_team')}"
    await message.answer(text, reply_markup=registration_nav_kb(step=4))


async def go_back(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    data = await state.get_data()

    if current == Registration.team.state:
        await state.set_state(Registration.birth_date)
        await prompt_birth_date(message, state)
    elif current == Registration.birth_date.state:
        pending = data.get("pending_calendar_month")
        if pending:
            await state.update_data(pending_calendar_month=None)
            await prompt_birth_date(message, state)
        else:
            await state.set_state(Registration.last_name)
            first_name = data.get("first_name", "")
            await prompt_last_name(message, first_name=first_name)
    elif current == Registration.last_name.state:
        await state.set_state(Registration.first_name)
        await prompt_first_name(message)
    else:
        await state.clear()
        await show_welcome(message)


async def cancel_registration(message: Message, state: FSMContext) -> None:
    await state.clear()
    from bot.keyboards import start_registration_kb

    await message.answer(get("registration.canceled"), reply_markup=start_registration_kb())
