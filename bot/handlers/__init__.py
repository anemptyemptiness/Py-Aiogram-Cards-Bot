from bot.handlers.user_handlers import startup_router
from bot.handlers.user_handlers import mini_dialog_router
from bot.handlers.user_handlers import menu_router
from bot.handlers.user_handlers import crystal_per_day_router
from bot.handlers.user_handlers import crystal_3_router
from bot.handlers.user_handlers import crystal_5_router
from bot.handlers.user_handlers import crystal_question_router
from bot.handlers.user_handlers import utils_router
from bot.handlers.admin_handlers import admin_startup_router
from bot.handlers.admin_handlers import premium_router
from bot.handlers.admin_handlers import statistics_router
from bot.handlers.admin_handlers import adv_router

__all__ = [
    "startup_router",
    "mini_dialog_router",
    "menu_router",
    "crystal_per_day_router",
    "crystal_3_router",
    "crystal_5_router",
    "crystal_question_router",
    "utils_router",
    "premium_router",
    "admin_startup_router",
    "statistics_router",
    "adv_router",
]
