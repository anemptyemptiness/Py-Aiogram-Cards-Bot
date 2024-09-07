from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎Кристалл на день", callback_data="crystal_per_day")],
            [InlineKeyboardButton(text="💎Метод 3-х кристаллов", callback_data="crystal_3")],
            [InlineKeyboardButton(text="💎Метод 5-ти кристаллов", callback_data="crystal_5")],
            [InlineKeyboardButton(text="💎Кристалл на Ваш вопрос", callback_data="crystal_question")],
            [InlineKeyboardButton(text="⚡️Важность энергообмена", callback_data="energy_exchange")],
        ]
    )
