from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.invoices.requests import InvoicesDAO
from bot.fsm.fsm import GratitudeSG
from bot.utils.payment import generate_payment_link

router = Router(name="gratitude_router")


@router.message(StateFilter(GratitudeSG.gratitude), F.text)
async def gratitude_handler(message: Message, session: AsyncSession):
    try:
        cost = float(message.text)
    except ValueError:
        await message.answer(
            text="Я ожидаю от Вас ввода любой цифры или числа ❤️",
        )
    else:
        invoice_id = await InvoicesDAO.create_invoice(session=session)

        url = generate_payment_link(
            merchant_login=settings.ROBOKASSA_MERCHANT_LOGIN,
            merchant_password_1=settings.ROBOKASSA_PROD_PWD_1,
            cost=cost,
            number=invoice_id,
            description="Метод 3-х Кристаллов",
            shp_user_id=message.chat.id,
        )

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Благодарность от души", url=url))
        builder.row(InlineKeyboardButton(text="Изменить сумму 🔄", callback_data="gratitude_change_sum"))

        await message.answer(
            text="По кнопке ниже можно будет отправить благодарность ❤️",
            reply_markup=builder.as_markup(),
        )


@router.callback_query(StateFilter(GratitudeSG.gratitude), F.data == "gratitude_change_sum")
async def gratitude_change_sum_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="go_to_menu"))

    await callback.message.answer(
        text="Введите любую сумму в качестве благодарности ❤️",
    )


@router.message(StateFilter(GratitudeSG.gratitude))
async def warning_gratitude_handler(message: Message):
    await message.answer(
        text="Я ожидаю от Вас ввода любой цифры или числа ❤️",
    )