import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE


def today() -> date:
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def parse_birth_date(text: str) -> tuple[int, int] | None:
    text = text.strip().replace(" ", "")
    m = re.match(r"^(\d{1,2})[./](\d{1,2})$", text)
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    try:
        date(2000, month, day)
    except ValueError:
        return None
    return day, month


def format_birth_display(day: int, month: int) -> str:
    months = (
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    )
    return f"{day} {months[month - 1]}"


def format_birth_short(day: int, month: int) -> str:
    return f"{day:02d}.{month:02d}"


def next_birthday(day: int, month: int, ref: date | None = None) -> date:
    ref = ref or today()
    year = ref.year
    try:
        bday = date(year, month, day)
    except ValueError:
        bday = date(year, month, 28 if month == 2 else day)
    if bday < ref:
        year += 1
        try:
            bday = date(year, month, day)
        except ValueError:
            bday = date(year, month, 28 if month == 2 else day)
    return bday


def days_until_birthday(day: int, month: int, ref: date | None = None) -> int:
    ref = ref or today()
    return (next_birthday(day, month, ref) - ref).days


def event_year_key(user_id: int, bday: date) -> str:
    return f"{user_id}:{bday.isoformat()}"


def username_display(username: str | None, first_name: str) -> str:
    if username:
        return f"@{username.lstrip('@')}"
    return first_name


def congrats_variant(user_id: int, year: int) -> str:
    variants = ("birthday.congrats_a", "birthday.congrats_b", "birthday.congrats_c")
    return variants[(user_id + year) % 3]
