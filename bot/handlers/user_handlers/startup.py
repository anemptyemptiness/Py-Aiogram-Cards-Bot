from pathlib import Path

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import MiniDialogSG
from bot.handlers.user_handlers.helpers import is_user_in_payment

router = Router(name="startup_router")


@router.message(CommandStart())
async def start_first_time_handler(message: Message, session: AsyncSession, state: FSMContext):
    if await is_user_in_payment(state):
        pass
    else:
        user_telegram_id = message.from_user.id
        user = await UsersDAO.get_user(session=session, telegram_id=user_telegram_id)
        builder = InlineKeyboardBuilder()

        if not user:
            builder.row(InlineKeyboardButton(text="Вперед в путешествие✨", callback_data="greeting_btn"))

            await message.answer(
                text="Приветствую  Вас, мой дорогой друг!\n\n"
                     "Я приглашаю Вас в путешествие.\n" 
                     "Так долго я думала над созданием этого светлого пространства.\n\n"
                     "Однажды, создав колоду Кристаллов Крайона, я поняла, что бывают случаи, "
                     "когда мне нужна помощь Кристаллов, но у меня  в этот момент нет под рукой карт.\n\n"
                     "И тогда я решилась на создание этого светлого пространства.\n"
                     "Я наполнила его светом любви и с трепетом отношусь к каждому, кто сюда зашёл.",
                reply_markup=builder.as_markup(),
            )
            await UsersDAO.add_user(session=session, telegram_id=user_telegram_id, username=message.from_user.username)
            await state.set_state(MiniDialogSG.greeting)
        else:
            builder.row(InlineKeyboardButton(text="Что такое кристаллы? 💎", callback_data="what_is_crystal_btn_startup"))
            builder.row(InlineKeyboardButton(text="Главное меню 🏡", callback_data="go_to_menu"))
            builder.row(InlineKeyboardButton(text="Помощь ❤️", callback_data="help_btn"))

            if not user.username:
                text = 'Привет!'
            else:
                text = f'Привет, <a href="{message.from_user.url}">{user.username}</a>!'

            await message.answer(
                text=text,
                reply_markup=builder.as_markup(),
            )


@router.callback_query(F.data == "go_back_to_start_cmd")
async def go_back_to_start_cmd_handler(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Что такое кристаллы? 💎", callback_data="what_is_crystal_btn_startup"))
    builder.row(InlineKeyboardButton(text="Главное меню 🏡", callback_data="go_back_to_menu"))
    builder.row(InlineKeyboardButton(text="Помощь ❤️", callback_data="help_btn"))

    user_telegram_id = callback.message.chat.id
    user = await UsersDAO.get_user(session=session, telegram_id=user_telegram_id)

    if not user.username:
        text = 'Привет!'
    else:
        text = f'Привет, <b>{user.username}</b>!'

    await callback.message.answer(
        text=text,
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "what_is_crystal_btn_startup")
async def what_is_crystal_btn_startup_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Дальше ➡️", callback_data="go_to_second_history_msg"))

    await callback.message.answer_video(
        video=FSInputFile(path=Path("bot/videos/history_video.MP4")),
        caption="История Кристаллов началась еще во времена великих Атлантов в Атлантиде.\n\n"
                "Они являются реальными проявлениями действительности, обладают великой силой, "
                "невероятной энергией и даже способностью к излечиванию. "
                "Благодаря тому, что Кристаллы созданы из высочайшего чистого света, "
                "они являются отличными и одними из самых действенных средств для исправления множеств "
                "кармических проблем на уровне родовой энергетики.\n\n"
                "Каждый Кристалл подчиняется божествам, имеет определенное число соответствия "
                "и даже обладает своим собственным подсознанием. "
                "На данный период времени Кристаллы сохранились и находятся в одном из помещений "
                "пирамиды под названием Гиза, которое еще не открыто.\n\n",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "go_to_second_history_msg")
async def go_to_second_history_msg_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться в меню", callback_data="go_back_to_start_cmd"))

    await callback.message.edit_caption(
        caption="Кристаллы - это матрицы Вселенной, хранящие высокие вибрации. "  
                "Вы открываете для себя необычную библиотеку новых знаний. Кристаллы вам покажут историю " 
                "в картинках, и дадут такую информацию, которую Вы нигде не получите. При получении " 
                "Кристаллической энергии информация передаётся языком Света, пакетами световых импульсов. "
                "Кристаллы активируют усилия работников Света, и постепенно меняют жизнь " 
                "человечества, поддерживая ежедневные позитивные мысли и эмоции. При "
                "соприкосновении с энергетическими полями способствуют скорейшей материализации " 
                "ваших намерений и мыслеформ.",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == "help_btn")
async def help_btn_handler(callback: CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="go_back_to_start_cmd"))

    await callback.message.edit_text(
        text="Если у вас возникли технические сложности, "
             "Вы можете написать мне и мы решим их в кратчайшие сроки.\n\n"
             "Благодарю ❤️\n\n"
             "<b><em>Телеграм</em></b>🔗: @Butakova_T",
        reply_markup=builder.as_markup(),
    )
