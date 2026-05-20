from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.texts import get


def start_registration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get("start.button_start"), callback_data="reg:start")]
        ]
    )


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
