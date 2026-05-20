from aiogram import Router

from bot.handlers.common import router as common_router
from bot.handlers.group import router as group_router
from bot.handlers.profile import router as profile_router
from bot.handlers.registration import router as registration_router
from bot.handlers.reminders import router as reminders_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(registration_router)
    root.include_router(profile_router)
    root.include_router(reminders_router)
    root.include_router(group_router)
    root.include_router(common_router)
    return root
