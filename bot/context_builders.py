from bot.database import User
from bot.utils import format_birth_display, format_birth_short, username_display


def user_context(user: User, bot_username: str = "") -> dict:
    bd = format_birth_display(user.birth_day, user.birth_month)
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "birth_date_display": bd,
        "birth_date_short": format_birth_short(user.birth_day, user.birth_month),
        "team": user.team,
        "username_display": username_display(user.username, user.first_name),
        "bot_username": f"@{bot_username}" if bot_username else "бота",
    }


def initiator_display(initiator: User | None) -> str:
    if not initiator:
        return "коллега"
    return username_display(initiator.username, initiator.first_name)
