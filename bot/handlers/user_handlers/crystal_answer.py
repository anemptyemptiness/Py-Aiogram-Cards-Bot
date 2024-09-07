import asyncio
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
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot import settings
from bot.db.buys.requests import BuysDAO
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import MenuSG, CardQuestionSG

router = Router(name="crystal_question_router")


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "crystal_question")
async def crystal_question_command(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    info_text = ("<b>Ответ на вопрос 💎</b>\n\n"
                 "Сконцентрировавшись на своей сегодняшней ситуации, "
                 "на вопросе, который волнует, или на том, что сейчас важно и актуально")
    telegram_id = callback.message.chat.id

    await callback.message.delete_reply_markup()
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)
    builder = InlineKeyboardBuilder()

    if user.free_cards > 0:
        builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_question"))
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
            title="Ответ на вопрос 💎",
            description="Ответ на вопрос 💎",
            payload="crystal_question_payment",
            currency="rub",
            prices=[
                LabeledPrice(label="Ответ на вопрос 💎", amount=15000),
            ],
            start_parameter="crystal_question_subscription",
            provider_token=settings.YOOTOKEN,
            reply_markup=builder.as_markup(),
        )
        await state.set_state(CardQuestionSG.payment)
    await callback.answer()


@router.callback_query(StateFilter(MenuSG.in_menu), F.data == "go_next_crystal_question")
async def go_next_crystal_question_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = callback.message.chat.id
    await callback.message.delete_reply_markup()

    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)
    await UsersDAO.update_user(session=session, telegram_id=telegram_id, free_cards=user.free_cards - 1)

    await callback.message.answer(
        text="⚠️ Вы израсходовали 1 бесплатный расклад\n\n"
             f"<b><em>Осталось бесплатных раскладов</em></b>: {user.free_cards}"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Я готов✔️", callback_data="i_am_ready"))

    await callback.message.answer(
        text="Приготовьтесь задать свой вопрос, чтобы он проявился в нашей реальности\n\n"
             'Когда Вы будете готовы его написать, нажмите на кнопку <b><em>"Я готов✔️"</em></b>',
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CardQuestionSG.waiting_for_question)


@router.pre_checkout_query(StateFilter(CardQuestionSG.payment))
async def pre_checkout_handler(checkout: PreCheckoutQuery, session: AsyncSession):
    await BuysDAO.add_buy(
        session=session,
        telegram_id=checkout.from_user.id,
        total_amount=int(checkout.total_amount / 100),
    )
    await checkout.answer(ok=True)


@router.message(StateFilter(CardQuestionSG.payment), F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_handler(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Я готов✔️", callback_data="i_am_ready"))

    await message.answer(
        text="Приготовьтесь задать свой вопрос, чтобы он проявился в нашей реальности\n\n"
             'Когда Вы будете готовы его написать, нажмите на кнопку <b><em>"Я готов✔️"</em></b>',
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CardQuestionSG.waiting_for_question)


@router.callback_query(StateFilter(CardQuestionSG.waiting_for_question), F.data == "i_am_ready")
async def ready_to_ask_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Напишите мне свой вопрос сюда и Кристаллы ответят тебе!"
    )
    await state.set_state(CardQuestionSG.ask_question)
    await callback.answer()


@router.message(StateFilter(CardQuestionSG.ask_question), F.text)
async def question_handler(message: Message, state: FSMContext):
    await asyncio.sleep(3)  # имитация анализа вопроса от пользователя
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Я ознакомился✔️", callback_data="in_process_ok"))

    card_id = random.randint(1, 122)

    await message.answer_photo(
        photo=FSInputFile(path=Path(f"bot/images/cards/{card_id}.jpg")),
        caption="Кристаллы сонастроились с Вами и вот Ваш Кристалл",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CardQuestionSG.in_process)


@router.message(StateFilter(CardQuestionSG.ask_question))
async def warning_question_handler(message: Message):
    await message.answer(
        text="Я ожидаю от Вас вопрос\n"
             "Пожалуйста, напишите мне его в сообщении!",
    )


@router.callback_query(StateFilter(CardQuestionSG.in_process), F.data == "in_process_ok")
async def go_crystal_question_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await state.set_state(CardQuestionSG.ending)

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


@router.callback_query(StateFilter(CardQuestionSG.ending), F.data == "ending_ok")
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
