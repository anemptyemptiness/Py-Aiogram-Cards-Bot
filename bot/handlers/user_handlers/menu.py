from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.user_kb import create_menu_kb
from bot.fsm.fsm import MenuSG

router = Router(name="menu_router")


@router.message(Command(commands="menu"), StateFilter(default_state))
async def menu_command(message: Message, state: FSMContext):
    await message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.set_state(MenuSG.in_menu)


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "go_to_menu")
async def menu_callback_button_command(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await callback.answer()


@router.callback_query(~StateFilter(default_state), F.data == "go_back_to_menu")
async def go_back_to_menu_from_payment_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.set_state(MenuSG.in_menu)
    await callback.answer()


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "go_back_to_menu_from_energy")
async def go_back_to_menu_from_energy_command(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await callback.answer()


@router.message(Command(commands="consultation"))
async def consultation_handler(message: Message):
    await message.answer(
        text="<b>📝Консультация</b>\n\n"
             "Если Вам нужен индивидуальный расклад или толкования ваших Кристаллов, "
             "Вы всегда можете написать мне.\n"
             "С уважением, Татьяна!❤️\n\n"
             "<b><em>Телеграм</em></b>🔗: @Butakova_T",
    )


@router.message(Command(commands="support"))
async def support_handler(message: Message):
    await message.answer(
        text="<b>⚒Технические сложности</b>\n\n"
             "Если у вас возникли технические сложности, "
             "Вы можете написать мне и мы их решим в кратчайшие сроки.\n\n"
             "Благодарю ❤️\n\n"
             "<b><em>Телеграм</em></b>🔗: @Butakova_T",
    )


@router.message(Command(commands="site"))
async def site_handler(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Сайт основателя", url="https://www.shimaa.de/kristalle-der-wirklichkeit/"))

    await message.answer(
        text="<b>🔗Сайт</b>\n\n"
             "Ссылка на сайт основателя техники",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "energy_exchange")
async def energy_exchange_handler(callback: CallbackQuery):
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="go_back_to_menu_from_energy"))

    await callback.message.edit_text(
        text="<b>Важность энергообмена</b>\n\n"
             "Дорогие, во Вселенной существуют принципы энергетического обмена, благодаря которым "
             "всё Мироздание существует и сохраняется в гармонии и балансе. "
             "Если мы получаем энергию (через консультации или сеансы), то должны вернуть её, "
             "чтобы сохранить гармонию, а также чтобы не включился закон сохранения баланса. "
             "Поэтому я устанавливаю символическую цену, чтобы поддерживать энергообмен. "
             "Таким образом мы сохраним баланс и гармонию для друг друга.\n\n"
             "С любовью и заботой о Вас! ❤️",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
