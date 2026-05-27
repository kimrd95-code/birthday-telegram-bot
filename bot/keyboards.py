import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.texts import get


def start_registration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get("start.button_start"), callback_data="reg:start")]
        ]
    )


def registration_nav_kb(*, step: int) -> InlineKeyboardMarkup:
    row: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=get("registration.button_cancel"), callback_data="reg:cancel"),
    ]
    if step > 1:
        row.insert(
            0,
            InlineKeyboardButton(text=get("registration.button_back"), callback_data="reg:back"),
        )
    return InlineKeyboardMarkup(inline_keyboard=[row])


def birth_months_kb(*, show_back: bool) -> InlineKeyboardMarkup:
    labels = [
        (1, "Янв"),
        (2, "Фев"),
        (3, "Мар"),
        (4, "Апр"),
        (5, "Май"),
        (6, "Июн"),
        (7, "Июл"),
        (8, "Авг"),
        (9, "Сен"),
        (10, "Окт"),
        (11, "Ноя"),
        (12, "Дек"),
    ]
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, 12, 4):
        chunk = labels[i : i + 4]
        rows.append(
            [
                InlineKeyboardButton(text=label, callback_data=f"reg:month:{num}")
                for num, label in chunk
            ]
        )
    nav = registration_nav_kb(step=3) if show_back else None
    if nav:
        rows.extend(nav.inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def birth_days_kb(month: int, *, show_back: bool) -> InlineKeyboardMarkup:
    last_day = calendar.monthrange(2000, month)[1]
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for day in range(1, last_day + 1):
        row.append(
            InlineKeyboardButton(text=str(day), callback_data=f"reg:day:{day}")
        )
        if len(row) == 7:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if show_back:
        rows.extend(registration_nav_kb(step=3).inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_chat_kb(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get("reminder.button_create_chat"),
                    callback_data=f"chat:create:{event_id}",
                )
            ]
        ]
    )


def join_chat_kb(invite_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get("reminder.button_join_chat"),
                    url=invite_link,
                )
            ]
        ]
    )


def cancel_initiator_kb(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get("initiator.button_cancel"),
                    callback_data=f"chat:cancel:{event_id}",
                )
            ]
        ]
    )


def profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get("profile.button_first_name"), callback_data="prof:first_name"),
                InlineKeyboardButton(text=get("profile.button_last_name"), callback_data="prof:last_name"),
            ],
            [
                InlineKeyboardButton(text=get("profile.button_birth_date"), callback_data="prof:birth_date"),
                InlineKeyboardButton(text=get("profile.button_team"), callback_data="prof:team"),
            ],
        ]
    )
