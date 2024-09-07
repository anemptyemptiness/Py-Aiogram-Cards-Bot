from bot.handlers.user_handlers.startup import router as startup_router
from bot.handlers.user_handlers.mini_dialog import router as mini_dialog_router
from bot.handlers.user_handlers.menu import router as menu_router
from bot.handlers.user_handlers.crystal_per_day import router as crystal_per_day_router
from bot.handlers.user_handlers.crystal_3 import router as crystal_3_router
from bot.handlers.user_handlers.crystal_5 import router as crystal_5_router
from bot.handlers.user_handlers.crystal_answer import router as crystal_question_router
from bot.handlers.user_handlers.utils import router as utils_router

__all__ = [
    "startup_router",
    "menu_router",
    "mini_dialog_router",
    "crystal_per_day_router",
    "crystal_3_router",
    "crystal_5_router",
    "crystal_question_router",
    "utils_router",
]
