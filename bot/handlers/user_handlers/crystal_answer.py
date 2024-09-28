import asyncio
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
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import CardQuestionSG
from bot.utils.payment import generate_payment_link

router = Router(name="crystal_question_router")


@router.callback_query(F.data == "crystal_question")
async def crystal_question_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    info_text = ("<b>Ответ на вопрос 💎</b>\n\n"
                 "Сконцентрировавшись на своей сегодняшней ситуации, "
                 "на вопросе, который волнует, или на том, что сейчас важно и актуально")

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_energy_question"))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="go_back_to_menu"))

    await callback.message.answer(
        text=f"{info_text}",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(CardQuestionSG.in_process)


@router.callback_query(StateFilter(CardQuestionSG.in_process), F.data == "go_next_energy_question")
async def go_next_energy_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_next_crystal_question"))

    await callback.message.answer(
        text="<b>Важность энергообмена</b>\n\n"
             "Дорогие, во Вселенной существуют принципы энергетического обмена, благодаря которым "
             "всё Мироздание существует и сохраняется в гармонии и балансе. "
             "Если мы получаем энергию (через консультации или сеансы), то должны вернуть её, "
             "чтобы сохранить гармонию, а также чтобы не включился закон сохранения баланса. "
             "Поэтому я устанавливаю символическую цену, чтобы поддерживать энергообмен. "
             "Таким образом мы сохраним баланс и гармонию для друг друга.\n"
             "С любовью и заботой о Вас! ❤️\n\n"
             "‼️По завершению у вас будет возможность поблагодарить от души в размере той суммы, которой пожелаете.",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(CardQuestionSG.in_process), F.data == "go_next_crystal_question")
async def go_next_crystal_question_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.delete_reply_markup()

    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    if user.free_cards > 0:
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


@router.callback_query(StateFilter(CardQuestionSG.waiting_for_question), F.data == "i_am_ready")
async def ready_to_ask_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Напишите мне свой вопрос сюда и Кристаллы ответят Вам!"
    )
    await state.set_state(CardQuestionSG.ask_question)


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
async def in_process_ok_command(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

    if not user.free_cards:
        builder.row(InlineKeyboardButton(text="Благодарность от души", callback_data="own_pay"))
        await state.set_state(CardQuestionSG.thankful)
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


@router.callback_query(StateFilter(CardQuestionSG.thankful), F.data == "own_pay")
async def own_pay_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        text="Введите любую сумму в качестве благодарности ❤️",
    )


@router.message(StateFilter(CardQuestionSG.thankful), F.text)
async def thankful_payment_handler(message: Message, session: AsyncSession):
    try:
        cost = float(message.text)
    except ValueError:
        await message.answer(
            text="Я ожидаю от Вас ввода любой цифры или числа ❤️",
        )
    else:
        telegram_id = message.chat.id
        user = await UsersDAO.get_user(session=session, telegram_id=telegram_id)

        url = generate_payment_link(
            merchant_login=settings.ROBOKASSA_MERCHANT_LOGIN,
            merchant_password_1=settings.ROBOKASSA_TEST_PWD_1,
            cost=cost,
            number=user.inv_number,
            description="Метод 3-х Кристаллов",
            shp_user_id=message.chat.id,
        )

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Благодарность от души", url=url))
        builder.row(InlineKeyboardButton(text="Изменить сумму 🔄", callback_data="own_pay"))

        await message.answer(
            text="По кнопке ниже можно будет отправить благодарность ❤️",
            reply_markup=builder.as_markup(),
        )
