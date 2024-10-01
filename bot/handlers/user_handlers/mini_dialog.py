from pathlib import Path

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.fsm.fsm import MiniDialogSG

router = Router(name="mini_dialog_router")


@router.callback_query(StateFilter(MiniDialogSG.greeting), F.data == "greeting_btn")
async def greeting_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text="Приветствую, мой дорогой друг!\n\n"
             "Я приглашаю Вас в путешествие. Так долго я думала над созданием этого светлого пространства.\n\n"
             "Однажды, создав колоду Кристаллов Крайона, я поняла, что есть моменты, когда мне нужна их помощь.\n\n"
             "И тогда я решилась на создание этого светлого места.\n"
             "Я наполнила его светом всеобъемлющий любви и с трепетом отношусь к каждому, кто сюда зашёл.\n\n"
             "<b>➢ Вперед в путешествие✨</b>"
    )

    await callback.message.answer(
        text="Давайте знакомиться!😊\nКак Вас зовут?"
    )
    await state.set_state(MiniDialogSG.name)
    await callback.answer()


@router.message(StateFilter(MiniDialogSG.name), F.text)
async def name_command(message: Message, state: FSMContext):
    user_name = message.text.strip()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="История Кристаллов Крайона", callback_data="what_is_crystal_history_btn"))

    await state.update_data(name=user_name)
    await message.answer(
        text=f"Очень приятно, {user_name}🥰\n"
             "Меня зовут Татьяна\n"
             "Сейчас я познакомлю Вас с Кристаллами Крайона💎\n\n"
             'Во время всего путешествия, если у Вас будут вопросы, '
             'Вы всегда можете обратится ко мне, нажав на кнопку <b>"Помощь ❤️"</b> и я с удовольствием Вам помогу',
        reply_markup=builder.as_markup(),
    )
    await state.set_state(MiniDialogSG.story_crystal)


@router.callback_query(StateFilter(MiniDialogSG.story_crystal), F.data == "what_is_crystal_history_btn")
async def what_is_crystal_history_command(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.delete_reply_markup()
    await callback.message.edit_text(
        text=f"Очень приятно, {data['name']}🥰\n"
             "Меня зовут Татьяна\n"
             "Сейчас я познакомлю Вас с Кристаллами Крайона💎\n\n"
             'Во время всего путешествия, если у Вас будут вопросы, '
             'Вы всегда можете обратится ко мне, нажав на кнопку <b>"Помощь ❤️"</b> и я с удовольствием Вам помогу\n\n'
             '<b>➢ История Кристаллов Крайона</b>'
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="А что такое Кристаллы?", callback_data="what_is_crystal_btn"))

    await callback.message.answer_video(
        caption="История Кристаллов началась еще во времена великих Атлантов в Атлантиде.\n\n"
                "Они являются реальными проявлениями действительности, обладают великой силой, "
                "невероятной энергией и даже способностью к излечиванию. "
                "Благодаря тому, что Кристаллы созданы из высочайшего чистого света, "
                "они являются отличными и одними из самых действенных средств для исправления множеств "
                "кармических проблем на уровне родовой энергетики.\n\n"
                "Каждый Кристалл подчиняется божествам, имеет определенное число соответствия "
                "и даже обладает своим собственным подсознанием. "
                "На данный период времени Кристаллы сохранились и находятся в одном из помещений "
                "пирамиды под названием Гиза, которое еще не открыто",
        video=FSInputFile(path=Path("bot/videos/history_video.mp4")),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(MiniDialogSG.what_is_crystal)
    await callback.answer()


@router.callback_query(StateFilter(MiniDialogSG.what_is_crystal), F.data == "what_is_crystal_btn")
async def what_is_crystal_command_again(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_caption(
        caption="История Кристаллов началась еще во времена великих Атлантов в Атлантиде.\n\n"
                "Они являются реальными проявлениями действительности, обладают великой силой, "
                "невероятной энергией и даже способностью к излечиванию. "
                "Благодаря тому, что Кристаллы созданы из высочайшего чистого света, "
                "они являются отличными и одними из самых действенных средств для исправления множеств "
                "кармических проблем на уровне родовой энергетики.\n\n"
                "Каждый Кристалл подчиняется божествам, имеет определенное число соответствия "
                "и даже обладает своим собственным подсознанием. "
                "На данный период времени Кристаллы сохранились и находятся в одном из помещений "
                "пирамиды под названием Гиза, которое еще не открыто\n\n"
                "<b>➢ А что такое Кристаллы?</b>",
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data="go_to_menu"))

    await callback.message.answer(
        text="Кристаллы - это матрицы Вселенной, хранящие высокие вибрации. "  
             "Вы открываете для себя необычную библиотеку новых знаний. Кристаллы вам покажут историю " 
             "в картинках, и дадут такую информацию, которую Вы нигде не получите. При получении " 
             "Кристаллической энергии информация передаётся языком Света, пакетами световых импульсов. "
             "Кристаллы активируют усилия работников Света, и постепенно меняют жизнь " 
             "человечества, поддерживая ежедневные позитивные мысли и эмоции. При "
             "соприкосновении с энергетическими полями способствуют скорейшей материализации " 
             "ваших намерений и мыслеформ\n\n"
             "<b>Я предлагаю Вам несколько способов взаимодействия с Кристаллами Крайона</b>",
        reply_markup=builder.as_markup(),
    )
    await state.clear()
    await callback.answer()
