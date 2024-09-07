from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_admin_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Пользователи", callback_data="adm_check_users")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats")],
            [InlineKeyboardButton(text="💰 Создать рекламу", callback_data="adm_adv")],
            [InlineKeyboardButton(text="◀️ Главное меню", callback_data="go_back_to_menu")],
        ]
    )
