import random
from decimal import Decimal
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
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import CardThreeSG
from bot.keyboards.user_kb import create_menu_kb
from bot.utils.payment import generate_payment_link

router = Router(name="crystal_3_router")


async def start_card_method(builder: InlineKeyboardBuilder, message: Message, state: FSMContext):
    builder.row(InlineKeyboardButton(text="Я ознакомился✔️", callback_data="in_process_ok"))

    cards_id = list()

    while True:
        if len(cards_id) == 3:
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
    await state.set_state(CardThreeSG.in_process)


@router.callback_query(F.data == "crystal_3")
async def crystal_3_command(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    info_text = ("<b>Метод 3-х Кристаллов 💎</b>\n\n"
                 "1 Кристалл: Кристалл необходимый для меня сейчас\n"
                 "2 Кристалл: Кристалл помогающий понять нынешнюю ситуацию и изменить ее в данных условиях\n"
                 "3 Кристалл: Кристалл помогающий мне стабилизировать мою энергию")

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_energy"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

    await callback.message.answer(
        text=f"{info_text}",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "go_next_energy")
async def go_next_energy_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_3"))

    await callback.message.answer(
        text="<b>Важность энергообмена</b>\n\n"
             "Дорогие, во Вселенной существуют принципы энергетического обмена, благодаря которым "
             "всё Мироздание существует и сохраняется в гармонии и балансе. "
             "Если мы получаем энергию (через консультации или сеансы), то должны вернуть её, "
             "чтобы сохранить гармонию, а также чтобы не включился закон сохранения баланса. "
             "Поэтому я устанавливаю символическую цену, чтобы поддерживать энергообмен. "
             "Таким образом мы сохраним баланс и гармонию для друг друга.\n"
             "С любовью и заботой о Вас! ❤️\n\n"
             "‼️По завершению мы просим Вас пожертвовать какую-то сумму (текст поменяем)",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "go_next_crystal_3")
async def go_next_crystal_3_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.delete_reply_markup()

    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    builder = InlineKeyboardBuilder()

    if user.free_cards > 0:
        await UsersDAO.update_user(session=session, telegram_id=telegram_id, free_cards=user.free_cards - 1)

        await callback.message.answer(
            text="⚠️ Вы израсходовали 1 бесплатный расклад\n\n"
                 f"<b><em>Осталось бесплатных раскладов</em></b>: {user.free_cards}"
        )
    await start_card_method(builder, callback.message, state)


@router.callback_query(StateFilter(CardThreeSG.in_process), F.data == "in_process_ok")
async def go_crystal_3_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await state.set_state(CardThreeSG.ending)

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


@router.callback_query(StateFilter(CardThreeSG.ending), F.data == "ending_ok")
async def in_process_ok_command(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    url = generate_payment_link(
        merchant_login=settings.ROBOKASSA_MERCHANT_LOGIN,
        merchant_password_1=settings.ROBOKASSA_TEST_PWD_1,
        cost=Decimal(150),
        number=user.inv_number,
        description="Метод 3-х Кристаллов",
        shp_user_id=callback.message.chat.id,
        )

    if not user.free_cards:
        builder.row(InlineKeyboardButton(text="Благодарность от души", url=url))
    else:
        builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data="go_to_menu"))
        await state.clear()

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


@router.callback_query(F.data == "go_after_payment")
async def go_after_payment_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.clear()
