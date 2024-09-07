from bot.handlers.admin_handlers.startup import router as admin_startup_router
from bot.handlers.admin_handlers.premium import router as premium_router
from bot.handlers.admin_handlers.statistics import router as statistics_router
from bot.handlers.admin_handlers.adv import router as adv_router

__all__ =[
    "admin_startup_router",
    "premium_router",
    "statistics_router",
    "adv_router",
]