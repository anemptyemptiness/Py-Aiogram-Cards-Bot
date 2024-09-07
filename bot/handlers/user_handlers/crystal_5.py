import random
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    Message,
    FSInputFile,
    InputMediaPhoto,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot import settings
from bot.db.buys.requests import BuysDAO
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import MenuSG, CardFiveSG

router = Router(name="crystal_5_router")


async def start_card_method(builder: InlineKeyboardBuilder, message: Message, state: FSMContext):
    builder.row(InlineKeyboardButton(text="Я ознакомился✔️", callback_data="in_process_ok"))

    cards_id = list()

    while True:
        if len(cards_id) == 5:
            break

        card_id = random.randint(1, 122)
        if card_id not in cards_id:
            cards_id.append(card_id)

    cards = [
        InputMediaPhoto(
            media=FSInputFile(path=Path(f"bot/images/cards/{card}.jpg")),
            caption="Это Ваши Кристаллы!" if not i else ""
        ) for i, card in enumerate(cards_id)
    ]

    await message.bot.send_media_group(
        chat_id=message.chat.id,
        media=cards,
    )
    await message.answer(
        text="Ознакомьтесь с Вашими Кристаллами",
        reply_markup=builder.as_markup()
    )
    await state.set_state(CardFiveSG.in_process)


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "crystal_5")
async def crystal_5_command(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    info_text = ("<b>Метод 5-ти Кристаллов 💎</b>\n\n"
                 "1 Кристалл: Кристалл, необходимый для моего физического тела\n" 
                 "2 Кристалл: Кристалл, необходимый для моего эмоционального тела\n"
                 "3 Кристалл: Кристалл, необходимый для моего ментального тела\n"
                 "4 Кристалл: Первоначальная энергия, которая меня сдерживает\n"
                 "5 Кристалл: Кристалл, необходимый для моего духовного развития")
    telegram_id = callback.message.chat.id

    await callback.message.delete_reply_markup()
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)
    builder = InlineKeyboardBuilder()

    if user.free_cards > 0:
        builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_5"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

        await callback.message.answer(
            text=f"{info_text}",
            reply_markup=builder.as_markup()
        )
    else:
        builder.add(InlineKeyboardButton(text="Оплатить 150 рублей", pay=True))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

        await callback.message.answer(
            text=f"{info_text}",
        )
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Метод 5-ти Кристаллов 💎",
            description="Метод 5-ти Кристаллов 💎",
            payload="crystal_5_payment",
            currency="rub",
            prices=[
                LabeledPrice(label="Метод 5-ти Кристаллов 💎", amount=15000),
            ],
            start_parameter="crystal_5_subscription",
            provider_token=settings.YOOTOKEN,
            reply_markup=builder.as_markup(),
        )
        await state.set_state(CardFiveSG.payment)
    await callback.answer()


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "go_next_crystal_5")
async def go_next_crystal_5_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
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


@router.pre_checkout_query(StateFilter(CardFiveSG.payment))
async def pre_checkout_handler(checkout: PreCheckoutQuery, session: AsyncSession):
    await BuysDAO.add_buy(
        session=session,
        telegram_id=checkout.from_user.id,
        total_amount=int(checkout.total_amount / 100),
    )
    await checkout.answer(ok=True)


@router.message(StateFilter(CardFiveSG.payment), F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_handler(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    await start_card_method(builder, message, state)


@router.callback_query(StateFilter(CardFiveSG.in_process), F.data == "in_process_ok")
async def go_crystal_5_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await state.set_state(CardFiveSG.ending)

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


@router.callback_query(StateFilter(CardFiveSG.ending), F.data == "ending_ok")
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
    await state.set_state(MenuSG.in_menu)
