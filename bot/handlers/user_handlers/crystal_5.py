import random
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message,
    FSInputFile,
    InputMediaPhoto,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.invoices.requests import InvoicesDAO
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import CardFiveSG
from bot.utils.payment import generate_payment_link

router = Router(name="crystal_5_router")


async def start_card_method(builder: InlineKeyboardBuilder, message: Message):
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


@router.callback_query(F.data == "crystal_5")
async def crystal_5_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    info_text = ("<b>Метод 5-ти Кристаллов 💎</b>\n\n"
                 "1 Кристалл: Кристалл, необходимый для моего физического тела\n" 
                 "2 Кристалл: Кристалл, необходимый для моего эмоционального тела\n"
                 "3 Кристалл: Кристалл, необходимый для моего ментального тела\n"
                 "4 Кристалл: Первоначальная энергия, которая меня сдерживает\n"
                 "5 Кристалл: Кристалл, необходимый для моего духовного развития")

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_energy_5"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

    await callback.message.answer(
        text=f"{info_text}",
        reply_markup=builder.as_markup(),
    )
    await state.clear()
    await state.set_state(CardFiveSG.in_process)


@router.callback_query(StateFilter(CardFiveSG.in_process), F.data == "go_next_energy_5")
async def go_next_energy_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_5"))

    await callback.message.answer(
        text="<b>Важность энергообмена ⚡️</b>\n\n"
             "Дорогие, во Вселенной существуют принципы энергетического обмена, "
             "благодаря которым всё Мироздание существует и сохраняется в гармонии и балансе. "
             "Если мы получаем энергию, то должны вернуть её, чтобы сохранить гармонию, "
             "а также чтобы не включился закон сохранения баланса. "
             'Поэтому я оставляю кнопку <b>"Благодарность от души"</b>, чтобы поддерживать энергообмен. '
             "Таким образом мы сохраним баланс и гармонию друг для друга. "
             "В конце сеанса у Вас будет кнопка с возможностью прислать Благодарность от души, "
             "не имеет значения, какая сумма это будет. Столько, сколько подскажет Вам душа.\n" 
             "Во Благо\n\n"
             "С любовью и заботой о Вас! ❤️",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(CardFiveSG.in_process), F.data == "go_next_crystal_5")
async def go_next_crystal_5_handler(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    await callback.message.delete_reply_markup()

    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    builder = InlineKeyboardBuilder()

    if user.free_cards > 0:
        user_free_cards = user.free_cards

        await callback.message.answer(
            text="⚠️ Вы израсходовали 1 бесплатный расклад\n\n"
                 f"<b><em>Осталось бесплатных раскладов</em></b>: {user_free_cards - 1}"
        )
    await start_card_method(builder, callback.message)


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
             "какой стороной Вы наложите его на себя, они найдут путь. "
             "Кристаллы Крайона посланы нам Светлыми Cилами для блага людей, "
             "поэтому при их использовании будет только благо, ошибки исключены.",
    )
    await callback.message.answer_photo(
        caption="Так же я советую Вам заземлиться с помощью Кристалла Арис. "
                "Это поможет энергии Кристаллов Крайона мягко и гармонично работать с вашим телом и душой.\n\n"
                "<b>Ознакомьтесь с Вашим Кристаллом и сонастройтесь с его энергией!</b>",
        photo=FSInputFile(path=Path("bot/images/cards/zazemlenie.jpg")),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(CardFiveSG.ending), F.data == "ending_ok")
async def in_process_ok_command(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    if not user.free_cards:
        builder.row(InlineKeyboardButton(text="Благодарность от души", callback_data="own_pay"))
        await state.set_state(CardFiveSG.thankful)
    else:
        await UsersDAO.update_user(session=session, telegram_id=telegram_id, free_cards=user.free_cards - 1)
        await UsersDAO.add_buy_by_user(session=session, telegram_id=telegram_id)
        builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="go_to_menu"))
        await state.clear()

    await callback.message.answer(
        text="<b>Благодарность Вселенной</b>\n\n"
             "После того как вы поработаете с картой, "
             "я предлагаю Вам пройти к закрытию пространства.\n"
             "Я благодарю Высшие силы в сопровождение. Высылаю Вам кристалл Благодарности. "
             "Просто сонастройтесь с ним и поблагодарите Всех. "
             "Пусть эти светлые энергии принесут Вам изобилие и гармонию во всем.",
    )
    await callback.message.answer_photo(
        caption="С Любовью и Благодарностью к Вам!❤️\n"
                "Я закрываю это пространство Во Благо Всем!❤️",
        photo=FSInputFile(path=Path("bot/images/cards/blagodarnost.jpg")),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(CardFiveSG.thankful), F.data == "own_pay")
async def own_pay_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Введите любую сумму в качестве благодарности ❤️",
    )


@router.message(StateFilter(CardFiveSG.thankful), F.text)
async def thankful_payment_handler(message: Message, session: AsyncSession):
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
            description="Метод 5-ти Кристаллов",
            shp_user_id=message.chat.id,
        )

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Благодарность от души", url=url))
        builder.row(InlineKeyboardButton(text="Изменить сумму 🔄", callback_data="own_pay"))

        await message.answer(
            text="По кнопке ниже можно будет отправить благодарность ❤️",
            reply_markup=builder.as_markup(),
        )
