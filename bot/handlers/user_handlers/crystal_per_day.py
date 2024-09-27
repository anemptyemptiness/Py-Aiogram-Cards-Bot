import random
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.buys.requests import BuysDAO
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import CardPerDaySG

router = Router(name="crystal_per_day_router")


async def start_card_method(builder: InlineKeyboardBuilder, message: Message, state: FSMContext):
    builder.row(InlineKeyboardButton(text="Я ознакомился✔️", callback_data="in_process_ok"))

    card_id = random.randint(1, 122)

    await message.answer_photo(
        caption="Это Ваша карта дня!",
        photo=FSInputFile(path=Path(f"bot/images/cards/{card_id}.jpg")),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CardPerDaySG.in_process)


@router.callback_query(F.data == "crystal_per_day")
async def crystal_per_day_command(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    info_text = ("<b>Кристалл на день 💎</b>\n\n"
                 "Вытяни символ на день, для прояснения жизненной ситуации, для медитации, "
                 "для использования энергии сегодня, "
                 "для использования энергии кристалла, для лечения себя и помощи другим людям.")
    telegram_id = callback.message.chat.id

    await callback.message.delete_reply_markup()
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)
    builder = InlineKeyboardBuilder()

    if user.free_cards > 0:
        builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_per_day"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

        await callback.message.answer(
            text=f"{info_text}",
            reply_markup=builder.as_markup(),
        )
    else:
        builder.add(InlineKeyboardButton(text="Оплатить 150 рублей", pay=True))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

        await callback.message.answer(
            text=f"{info_text}",
        )
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Кристалл на день 💎",
            description="Кристалл на день 💎",
            payload="crystal_per_day_payment",
            currency="rub",
            prices=[
                LabeledPrice(label="Кристалл на день 💎", amount=15000),
            ],
            start_parameter="crystal_per_day_subscription",
            provider_token=settings.YOOTOKEN,
            reply_markup=builder.as_markup(),
        )
        await state.set_state(CardPerDaySG.payment)
    await callback.answer()


@router.callback_query(F.data == "go_next_crystal_per_day")
async def go_next_crystal_per_day_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete_reply_markup()
    telegram_id = callback.message.chat.id
    builder = InlineKeyboardBuilder()

    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)
    await UsersDAO.update_user(session=session, telegram_id=telegram_id, free_cards=user.free_cards - 1)

    await callback.message.answer(
        text="⚠️ Вы израсходовали 1 бесплатный расклад\n\n"
             f"<b><em>Осталось бесплатных раскладов</em></b>: {user.free_cards}"
    )
    await start_card_method(builder, callback.message, state)


@router.pre_checkout_query(StateFilter(CardPerDaySG.payment))
async def pre_checkout_handler(checkout: PreCheckoutQuery, session: AsyncSession):
    await BuysDAO.add_buy(
        session=session,
        telegram_id=checkout.from_user.id,
        total_amount=int(checkout.total_amount / 100),
    )
    await checkout.answer(ok=True)


@router.message(StateFilter(CardPerDaySG.payment), F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_handler(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    await start_card_method(builder, message, state)


@router.callback_query(StateFilter(CardPerDaySG.in_process), F.data == "in_process_ok")
async def go_crystal_per_day_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await state.set_state(CardPerDaySG.ending)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Готово✔️", callback_data="ending_ok"))

    await callback.message.answer(
        text="<b>Сила Кристаллов Крайона</b>\n\n"
             "Доверяйте подсказками своей души при работе с Кристаллами Крайона. "
             "Вы можете представить их образ, нарисовать или проговорить их имя. Можно напечатать и заряжать воду. "
             "Или мысленно помещать их в свою ауру. " 
             "Можно посылать Кристаллы мысленно через время и пространство любимым и близким людям "
             "для их исцеления и блага (запрашивая при этом медитативно согласие их Высшего Я). "
             "У Кристаллов есть своё сознание, поэтому не важно, "
             "какой стороной вы наложите его на себя, они найдут путь. "
             "Кристаллы Крайона посланы нам Светлыми Cилами для блага людей, "
             "поэтому при их использовании будет только благо, ошибки исключены.",
    )
    await callback.message.answer_photo(
        caption="Так же я советую Вам заземлиться с помощью Кристалла Арис. "
                "Это поможет энергии Кристаллов Крайона мягко и гармонично работать с вашем телом и душой.\n\n"
                "<b>Ознакомьтесь с Вашим Кристаллом и сонастройтесь с его энергией!</b>",
        photo=FSInputFile(path=Path("bot/images/cards/zazemlenie.jpg")),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(CardPerDaySG.ending), F.data == "ending_ok")
async def in_process_ok_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="go_to_menu"))

    await callback.message.answer(
        text="<b>Благодарность Вселенной</b>\n\n"
             "После того как вы поработаете с картой. "
             "Я предлагаю вам пройти к закрытию пространства.\n"
             "Я Благодарю Высшие силы в сопровождение. Высылаю Вам кристалл Благодарности. "
             "Просто сонастройтесь с ним и поблагодари Всех. "
             "Пусть эти светлые энергии принесут Вам изобилия и гармонию во всем.",
    )
    await callback.message.answer_photo(
        caption="С Любовью и Благодарностью к Вам!❤️\n"
                "Я закрываю это пространство Во Благо Всем!❤️",
        photo=FSInputFile(path=Path("bot/images/cards/blagodarnost.jpg")),
        reply_markup=builder.as_markup(),
    )
    await state.clear()
