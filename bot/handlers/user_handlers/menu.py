from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.fsm.fsm import GratitudeSG
from bot.handlers.user_handlers.helpers import is_user_in_payment
from bot.keyboards.user_kb import create_menu_kb

router = Router(name="menu_router")


@router.message(Command(commands="menu"))
async def menu_command(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        await message.answer(
            text="Вы находитесь в главном меню 🏡",
            reply_markup=create_menu_kb(),
        )
        await state.clear()


@router.callback_query(F.data == "go_to_menu")
async def menu_callback_button_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.clear()


@router.callback_query(F.data == "go_back_to_menu")
async def go_back_to_menu_from_payment_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.clear()


@router.message(Command(commands="consultation"))
async def consultation_handler(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
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
             "Если у Вас возникли технические сложности, "
             "Вы можете написать мне и мы их решим в кратчайшие сроки.\n\n"
             "Благодарю ❤️\n\n"
             "<b><em>Телеграм</em></b>🔗: @Butakova_T",
    )


@router.message(Command(commands="site"))
async def site_handler(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Сайт основателя", url="https://www.shimaa.de/kristalle-der-wirklichkeit/"))

        await message.answer(
            text="<b>🔗Сайт</b>\n\n"
                 "Ссылка на сайт основателя техники",
            reply_markup=builder.as_markup(),
        )


@router.message(Command(commands="oferta"))
async def oferta_command(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        await message.answer_document(
            document=FSInputFile(Path("bot/oferta/Оферта.docx")),
        )


@router.message(Command(commands="rules"))
async def rules_command(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        await message.answer(
            text="🧾 <b>Правила оформления заказа:</b>\n\n"
                 "После того как Вы выберете метод расклада карт и произведете оплату, "
                 "бот автоматически вышлет вам вашу карту (её расшифровку и инструкцию по использованию).\n"
                 "Если у Вас возникли вопросы, Вы всегда можете обратится в техническую поддержку.\n"
                 "Мы работаем для Вас 24/7."
        )


@router.message(Command(commands="gratitude"))
async def gratitude_command(message: Message, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="go_to_menu"))

        await message.answer(
            text="Введите любую сумму в качестве благодарности ❤️",
            reply_markup=builder.as_markup(),
        )
        await state.set_state(GratitudeSG.gratitude)
