import aiosqlite
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from config import DATABASE_PATH, INITIATOR_TIMEOUT_HOURS


@dataclass
class User:
    id: int
    telegram_id: int
    first_name: str
    last_name: str
    birth_day: int
    birth_month: int
    team: str
    username: str | None
    is_registered: bool


@dataclass
class BirthdayEvent:
    id: int
    birthday_user_id: int
    event_date: str
    year_key: str
    chat_id: int | None
    invite_link: str | None
    initiator_user_id: int | None
    chat_created_at: str | None
    reminder_7_sent: bool
    reminder_6_sent: bool
    reminder_4_sent: bool
    reminder_2_sent: bool
    not_joined_sent: bool
    birthday_congrats_sent: bool


async def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL DEFAULT '',
                last_name TEXT NOT NULL DEFAULT '',
                birth_day INTEGER,
                birth_month INTEGER,
                team TEXT NOT NULL DEFAULT '',
                username TEXT,
                is_registered INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS birthday_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                birthday_user_id INTEGER NOT NULL,
                event_date TEXT NOT NULL,
                year_key TEXT UNIQUE NOT NULL,
                chat_id INTEGER,
                invite_link TEXT,
                initiator_user_id INTEGER,
                chat_created_at TEXT,
                reminder_7_sent INTEGER NOT NULL DEFAULT 0,
                reminder_6_sent INTEGER NOT NULL DEFAULT 0,
                reminder_4_sent INTEGER NOT NULL DEFAULT 0,
                reminder_2_sent INTEGER NOT NULL DEFAULT 0,
                not_joined_sent INTEGER NOT NULL DEFAULT 0,
                birthday_congrats_sent INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (birthday_user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS pending_chat_creation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL UNIQUE,
                initiator_user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES birthday_events(id),
                FOREIGN KEY (initiator_user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS event_chat_members (
                event_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (event_id, user_id),
                FOREIGN KEY (event_id) REFERENCES birthday_events(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        await db.commit()


def _row_to_user(row: aiosqlite.Row) -> User:
    return User(
        id=row["id"],
        telegram_id=row["telegram_id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_day=row["birth_day"],
        birth_month=row["birth_month"],
        team=row["team"],
        username=row["username"],
        is_registered=bool(row["is_registered"]),
    )


def _row_to_event(row: aiosqlite.Row) -> BirthdayEvent:
    return BirthdayEvent(
        id=row["id"],
        birthday_user_id=row["birthday_user_id"],
        event_date=row["event_date"],
        year_key=row["year_key"],
        chat_id=row["chat_id"],
        invite_link=row["invite_link"],
        initiator_user_id=row["initiator_user_id"],
        chat_created_at=row["chat_created_at"],
        reminder_7_sent=bool(row["reminder_7_sent"]),
        reminder_6_sent=bool(row["reminder_6_sent"]),
        reminder_4_sent=bool(row["reminder_4_sent"]),
        reminder_2_sent=bool(row["reminder_2_sent"]),
        not_joined_sent=bool(row["not_joined_sent"]),
        birthday_congrats_sent=bool(row["birthday_congrats_sent"]),
    )


async def get_user_by_telegram(telegram_id: int) -> User | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            row = await cur.fetchone()
    return _row_to_user(row) if row else None


async def get_user_by_id(user_id: int) -> User | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
    return _row_to_user(row) if row else None


async def upsert_user_telegram(telegram_id: int, username: str | None) -> User:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            """
            INSERT INTO users (telegram_id, username)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET username = excluded.username
            """,
            (telegram_id, username),
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            row = await cur.fetchone()
    return _row_to_user(row)


async def save_registration(
    telegram_id: int,
    first_name: str,
    last_name: str,
    birth_day: int,
    birth_month: int,
    team: str,
    username: str | None,
) -> User:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            """
            UPDATE users SET
                first_name = ?, last_name = ?, birth_day = ?, birth_month = ?,
                team = ?, username = ?, is_registered = 1
            WHERE telegram_id = ?
            """,
            (first_name, last_name, birth_day, birth_month, team, username, telegram_id),
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            row = await cur.fetchone()
    return _row_to_user(row)


async def update_user_field(user_id: int, field: str, value: Any) -> None:
    allowed = {"first_name", "last_name", "birth_day", "birth_month", "team"}
    if field not in allowed:
        raise ValueError(field)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (value, user_id))
        await db.commit()


async def list_registered_users() -> list[User]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE is_registered = 1 ORDER BY id"
        ) as cur:
            rows = await cur.fetchall()
    return [_row_to_user(r) for r in rows]


async def get_or_create_event(birthday_user_id: int, event_date: str, year_key: str) -> BirthdayEvent:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM birthday_events WHERE year_key = ?", (year_key,)
        ) as cur:
            row = await cur.fetchone()
        if row:
            return _row_to_event(row)
        await db.execute(
            """
            INSERT INTO birthday_events (birthday_user_id, event_date, year_key)
            VALUES (?, ?, ?)
            """,
            (birthday_user_id, event_date, year_key),
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM birthday_events WHERE year_key = ?", (year_key,)
        ) as cur:
            row = await cur.fetchone()
    return _row_to_event(row)


async def get_event_by_id(event_id: int) -> BirthdayEvent | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM birthday_events WHERE id = ?", (event_id,)
        ) as cur:
            row = await cur.fetchone()
    return _row_to_event(row) if row else None


async def get_event_for_user_on_date(birthday_user_id: int, event_date: str) -> BirthdayEvent | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM birthday_events WHERE birthday_user_id = ? AND event_date = ?",
            (birthday_user_id, event_date),
        ) as cur:
            row = await cur.fetchone()
    return _row_to_event(row) if row else None


async def mark_reminder_flag(event_id: int, flag: str) -> None:
    allowed = {
        "reminder_7_sent",
        "reminder_6_sent",
        "reminder_4_sent",
        "reminder_2_sent",
        "not_joined_sent",
        "birthday_congrats_sent",
    }
    if flag not in allowed:
        raise ValueError(flag)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            f"UPDATE birthday_events SET {flag} = 1 WHERE id = ?", (event_id,)
        )
        await db.commit()


async def set_event_chat(
    event_id: int,
    chat_id: int,
    invite_link: str,
    initiator_user_id: int,
) -> None:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE birthday_events SET
                chat_id = ?, invite_link = ?, initiator_user_id = ?,
                chat_created_at = ?
            WHERE id = ?
            """,
            (chat_id, invite_link, initiator_user_id, now, event_id),
        )
        await db.execute(
            "DELETE FROM pending_chat_creation WHERE event_id = ?", (event_id,)
        )
        await db.commit()


async def create_pending(event_id: int, initiator_user_id: int) -> None:
    expires = (
        datetime.utcnow() + timedelta(hours=INITIATOR_TIMEOUT_HOURS)
    ).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM pending_chat_creation WHERE event_id = ?", (event_id,)
        )
        await db.execute(
            """
            INSERT INTO pending_chat_creation (event_id, initiator_user_id, expires_at)
            VALUES (?, ?, ?)
            """,
            (event_id, initiator_user_id, expires),
        )
        await db.commit()


async def get_pending_by_event(event_id: int) -> tuple[int, str] | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT initiator_user_id, expires_at FROM pending_chat_creation WHERE event_id = ?",
            (event_id,),
        ) as cur:
            row = await cur.fetchone()
    if not row:
        return None
    return row["initiator_user_id"], row["expires_at"]


async def get_pending_by_initiator(initiator_user_id: int) -> int | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT event_id FROM pending_chat_creation WHERE initiator_user_id = ?",
            (initiator_user_id,),
        ) as cur:
            row = await cur.fetchone()
    return row["event_id"] if row else None


async def cancel_pending(event_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM pending_chat_creation WHERE event_id = ?", (event_id,)
        )
        await db.commit()


async def clear_expired_pending() -> list[int]:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT event_id FROM pending_chat_creation WHERE expires_at < ?", (now,)
        ) as cur:
            rows = await cur.fetchall()
        ids = [r["event_id"] for r in rows]
        if ids:
            placeholders = ",".join("?" * len(ids))
            await db.execute(
                f"DELETE FROM pending_chat_creation WHERE event_id IN ({placeholders})",
                ids,
            )
            await db.commit()
    return ids


async def record_chat_member(event_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO event_chat_members (event_id, user_id)
            VALUES (?, ?)
            """,
            (event_id, user_id),
        )
        await db.commit()


async def is_member_of_event(event_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM event_chat_members WHERE event_id = ? AND user_id = ?",
            (event_id, user_id),
        ) as cur:
            row = await cur.fetchone()
    return row is not None


async def find_event_by_chat_id(chat_id: int) -> BirthdayEvent | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM birthday_events WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
            (chat_id,),
        ) as cur:
            row = await cur.fetchone()
    return _row_to_event(row) if row else None
