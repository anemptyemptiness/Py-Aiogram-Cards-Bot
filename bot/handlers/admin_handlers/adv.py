import json
from datetime import datetime, timezone, timedelta

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from nats.js import JetStreamContext

from bot.config import settings
from bot.callbacks.calendar import (
    YearToCallbackData,
    MonthToCallbackData,
    DayToCallbackData,
    HourToCallbackData,
    MinuteToCallbackData,
)
from bot.fsm.fsm import AdminSG, AdminAdvSG
from bot.handlers.admin_handlers.utils import get_month_kb, get_day_kb
from bot.keyboards.admin_kb import create_admin_kb
from bot.lexicon.lexicon_ru import MONTHS, MONTH_DAYS
from bot.services.adv.publisher import adv_publisher

router = Router(name="adv_router")


async def completed_adv(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    builder_adv = InlineKeyboardBuilder()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Всё корректно ✅", callback_data="adm_adv_correct"))
    builder.row(InlineKeyboardButton(text="Изменить текст сообщения 🔄", callback_data="adm_adv_change_msg_text"))

    if "url" in data:
        builder_adv.row(InlineKeyboardButton(text=f"{data['adv_url_text']}", url=f"{data['url']}"))

        builder.row(InlineKeyboardButton(
            text="Изменить название кнопки 🔄",
            callback_data="adm_adv_change_btn_name"
        ))
        builder.row(InlineKeyboardButton(
            text="Изменить ссылку кнопки 🔄",
            callback_data="adm_adv_change_btn_url")
        )

    if "adv_pictures" in data:
        builder.row(InlineKeyboardButton(text="Изменить картинки 🔄", callback_data="adm_adv_change_pics"))

        if isinstance(data["adv_pictures"], list):
            adv_pictures_media = [
                InputMediaPhoto(
                    media=photo_file_id,
                    caption=f"{data['adv_text']}" if not i else "",
                ) for i, photo_file_id in enumerate(data["adv_pictures"])
            ]

            await bot.send_media_group(
                chat_id=message.chat.id,
                media=adv_pictures_media,
            )
        elif isinstance(data["adv_pictures"], str):
            await message.answer_photo(
                photo=data["adv_pictures"],
                caption=f"{data['adv_text']}",
                reply_markup=builder_adv.as_markup(),
            )
    else:
        await message.answer(
            text=f"{data['adv_text']}",
            reply_markup=builder_adv.as_markup(),
        )

    builder.row(InlineKeyboardButton(text="Начать заново 🔄", callback_data="adm_adv"))
    await state.set_state(AdminSG.in_adm)
    await message.answer(
        text="Изучите рекламное сообщение, которое я отправил выше и проверьте, "
             "всё ли корректно?",
        reply_markup=builder.as_markup()
    )


async def start_creating_adv(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    dt_now = datetime.now(tz=timezone(timedelta(hours=3)))

    builder = InlineKeyboardBuilder()
    buttons = list()

    for year in range(dt_now.year, dt_now.year + 2):
        buttons.append(
            InlineKeyboardButton(
                text=f"{year}",
                callback_data=YearToCallbackData(
                    year_to=year,
                ).pack(),
            )
        )
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text="Выберите <b>год</b>, в <b>котором нужно отобразить рекламу</b>",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AdminAdvSG.adv)


@router.callback_query(StateFilter(AdminAdvSG.adv), F.data == "cancel")
async def cancel_adv_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await state.set_state(AdminSG.in_adm)
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv")
async def adm_adv_command(callback: CallbackQuery, state: FSMContext):
    await start_creating_adv(callback, state)
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), YearToCallbackData.filter())
async def select_year_to_adv_handler(
        callback: CallbackQuery,
        callback_data: YearToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(year_to=callback_data.year_to)

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>месяц</b>, в <b>котором нужно отобразить рекламу</b>",
        reply_markup=get_month_kb(builder=builder, cb_data=MonthToCallbackData, date_data=await state.get_data())
    )


@router.callback_query(StateFilter(AdminAdvSG.adv), MonthToCallbackData.filter())
async def select_month_to_handler(callback: CallbackQuery, callback_data: MonthToCallbackData, state: FSMContext):
    await state.update_data(month_to=callback_data.month_to)

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>день</b>, <b>в который будет отправлена реклама</b>",
        reply_markup=get_day_kb(builder=builder, cb_data=DayToCallbackData, date_data=await state.get_data()),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), DayToCallbackData.filter())
async def select_day_to_handler(callback: CallbackQuery, callback_data: DayToCallbackData, state: FSMContext):
    dt_now = datetime.now(tz=timezone(timedelta(hours=3)))
    await state.update_data(day_to=callback_data.day_to)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    buttons = list()

    if data["year_to"] == dt_now.year and data["month_to"] == dt_now.month and data["day_to"] == dt_now.day:
        start_hour = dt_now.hour
    else:
        start_hour = 0

    for hour in range(start_hour, 24):
        buttons.append(
            InlineKeyboardButton(
                text=f"{hour}",
                callback_data=HourToCallbackData(
                    hour_to=hour,
                ).pack(),
            )
        )
    builder.add(*buttons)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text="Выберите <b>час</b>, <b>в который будет отправлена реклама</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), HourToCallbackData.filter())
async def select_hour_to_handler(callback: CallbackQuery, callback_data: HourToCallbackData, state: FSMContext):
    dt_now = datetime.now(tz=timezone(timedelta(hours=3)))
    await state.update_data(hour_to=callback_data.hour_to)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    buttons = list()

    if (data["year_to"] == dt_now.year and
            data["month_to"] == dt_now.month and
            data["day_to"] == dt_now.day and
            data["hour_to"] == dt_now.hour):
        start_minute = dt_now.minute
    else:
        start_minute = 0

    for minute in range(start_minute, 59 + 1):
        buttons.append(
            InlineKeyboardButton(
                text=f"{minute}",
                callback_data=MinuteToCallbackData(
                    minute_to=minute,
                ).pack(),
            )
        )
    builder.add(*buttons)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text="Выберите, в какую <b>минуту</b> нужно <b>отправить рекламу</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), MinuteToCallbackData.filter())
async def select_minute_to_handler(callback: CallbackQuery, callback_data: MinuteToCallbackData, state: FSMContext):
    await state.set_state(AdminSG.in_adm)
    await state.update_data(minute_to=callback_data.minute_to)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Всё корректно ✅", callback_data="adm_adv_date_correct"))
    builder.row(InlineKeyboardButton(text="Начать заново 🔄", callback_data="adm_adv"))

    await callback.message.edit_text(
        text="Ваша выбранная дата:\n"
             f"<b>{data['day_to']} {MONTHS[data['month_to']]} {data['year_to']} "
             f"{'0' + str(data['hour_to']) if data['hour_to'] < 10 else data['hour_to']}:"
             f"{'0' + str(data['minute_to']) if data['minute_to'] < 10 else data['minute_to']}</b>\n\n"
             "Проверьте, корректно ли Вы выбрали дату?",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_date_correct")
async def adm_adv_date_correct_handler(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить картинку", callback_data="adm_adv_add_picture"))
    builder.row(InlineKeyboardButton(text="Без картинки", callback_data="adm_adv_no_picture"))

    await callback.message.edit_text(
        text="Нужно ли добавить картинку в рекламное сообщение?",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AdminAdvSG.adv)
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), F.data == "adm_adv_no_picture")
async def adm_adv_no_picture_handler(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить кнопку-ссылку", callback_data="adm_adv_add_link_btn"))
    builder.row(InlineKeyboardButton(text="Без кнопки-ссылки", callback_data="adm_adv_no_link_btn"))

    await callback.message.edit_text(
        text="Нужно ли добавить кнопку-ссылку в рекламное сообщение?",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AdminAdvSG.adv_url)
    await callback.answer()


@router.callback_query(StateFilter(AdminAdvSG.adv), F.data == "adm_adv_add_picture")
async def adm_adv_app_picture_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Отправьте мне картинки, которые я прикреплю к рекламному сообщению!",
    )
    await state.set_state(AdminAdvSG.adv_pictures)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_pictures))
async def adm_adv_select_pictures_handler(message: Message, state: FSMContext):
    if message.photo:
        if "adv_pictures" not in await state.get_data():
            await state.update_data(adv_pictures=message.photo[-1].file_id)

        builder = InlineKeyboardBuilder()
        data = await state.get_data()

        if isinstance(data["adv_pictures"], list):
            await message.answer(
                text="Отлично, я сохранил все картинки!\n\n"
                     "А теперь пришлите мне заранее отформатированный текст рекламного сообщения",
            )
            await state.set_state(AdminAdvSG.adv_text)
        else:
            builder.row(InlineKeyboardButton(text="Добавить кнопку-ссылку", callback_data="adm_adv_add_link_btn"))
            builder.row(InlineKeyboardButton(text="Без кнопки-ссылки", callback_data="adm_adv_no_link_btn"))

            await message.answer(
                text="Отлично, я сохранил картинку!\n\n"
                     "Хотите ли Вы добавить кнопку-ссылку в рекламное сообщение?",
                reply_markup=builder.as_markup(),
            )
            await state.set_state(AdminAdvSG.adv_url)
    else:
        await message.answer(
            text="Я ожидаю от Вас картинки для рекламного сообщения!",
        )


@router.callback_query(StateFilter(AdminAdvSG.adv_url), F.data == "adm_adv_add_link_btn")
async def adm_adv_add_link_btn_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Пришлите мне ссылку, которую нужно будет отобразить в кнопке рекламного сообщения",
    )
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_url))
async def adm_adv_select_link_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(url=message.text)
        await message.answer(
            text="Я сохранил ссылку!\n\n"
                 "А теперь пришлите мне название для кнопки-ссылки!",
        )
        await state.set_state(AdminAdvSG.adv_url_btn_name)
    else:
        await message.answer(
            text="Я ожидаю от Вас ссылку вида https://ваша_ссылка.com <b>в виде текста</b>",
        )


@router.message(StateFilter(AdminAdvSG.adv_url_btn_name))
async def adm_adv_change_btn_url_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(adv_url_text=message.text)
        await message.answer(
            text="А теперь пришлите мне заранее отформатированный текст рекламного сообщения",
        )
        await state.set_state(AdminAdvSG.adv_text)
    else:
        await message.answer(
            text="Я ожидаю от Вас <b>имя</b> кнопки-ссылки!\n\n"
                 "Не нужно присылать мне что-то, отличающееся от текстового сообщения",
        )


@router.callback_query(StateFilter(AdminAdvSG.adv_url), F.data == "adm_adv_no_link_btn")
async def adm_adv_no_link_btn_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="А теперь пришлите мне заранее отформатированный текст рекламного сообщения",
    )
    await state.set_state(AdminAdvSG.adv_text)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_text))
async def adm_adv_select_adv_text_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        data = await state.get_data()

        if isinstance(data.get("adv_pictures", None), list):
            await state.update_data(count_of_pics=len(data["adv_pictures"]))
        elif isinstance(data.get("adv_pictures", None), str):
            await state.update_data(count_of_pics=1)
        else:
            await state.update_data(count_of_pics=0)

        await state.update_data(old_pics=data.get("adv_pictures", None), adv_text=message.text)
        await completed_adv(message, state, bot)
    else:
        await message.answer(
            text="Я ожидаю от Вас заранее отформатированный <b>текст</b> рекламного сообщения!\n\n"
                 "Не нужно присылать мне что-то, отличающееся от текстового сообщения",
        )


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_correct")
async def adm_adv_completed_msg_handler(
        callback: CallbackQuery, state: FSMContext, js: JetStreamContext,
):
    data = await state.get_data()
    dt_send = datetime(
        year=data["year_to"],
        month=data["month_to"],
        day=data["day_to"],
        hour=data["hour_to"],
        minute=data["minute_to"],
        tzinfo=timezone(timedelta(hours=3)),
    )
    await adv_publisher(
        js=js,
        subject=settings.NATS_CONSUMER_SUBJECT_ADV,
        dt_send=dt_send.strftime("%Y-%m-%d %H:%M"),
        text=json.dumps(data.get("adv_text")),
        pictures=json.dumps(data.get("adv_pictures", None)),
        url=json.dumps(data.get("url", None)),
        url_text=json.dumps(data.get("adv_url_text", None)),
    )
    await callback.message.edit_text(
        text=f"✅ Отложенное сообщение запланировано на {dt_send.strftime('%Y-%m-%d %H:%M')}\n\n"
             "🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_change_msg_text")
async def adm_adv_change_msg_text_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Пришлите новый заранее отформатированный текст рекламного сообщения!",
    )
    await state.set_state(AdminAdvSG.adv_change_text)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_change_text))
async def adm_adv_change_text_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        await state.update_data(adv_text=message.text)
        await completed_adv(message, state, bot)
    else:
        await message.answer(
            text="Я ожидаю от Вас заранее отформатированный <b>текст</b> рекламного сообщения!\n\n"
                 "Не нужно присылать мне что-то, отличающееся от текстового сообщения",
        )


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_change_pics")
async def adm_adv_change_pics_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Пришлите новые картинки для рекламного сообщения!"
    )
    await state.set_state(AdminAdvSG.adv_change_pics)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_change_pics))
async def adm_adv_change_pics_handler(message: Message, state: FSMContext, bot: Bot):
    if message.photo:
        data = await state.get_data()

        if data["count_of_pics"] == 1 and isinstance(data["adv_pictures"], list) and data.get("url", None):
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Начать заново 🔄", callback_data="adm_adv_change_pics_cancel"))

            await state.update_data(adv_pictures=data["old_pics"])

            await message.answer(
                text="Ранее Вы присылали 1 картинку, а сейчас пытаетесь отправить более 1 картинки\n\n"
                     "🔴 Телеграм запрещает прикреплять любую кнопку, если в сообщении более 1 картинки\n"
                     "Если Вы хотите прикрепить более 1 картинки, то Вам нужно переделать рекламное сообщение\n\n"
                     "<em>⚠️Если Вы случайно ошиблись, то проигнорируйте это сообщение "
                     "и отправьте 1 новую картинку</em>\n\n"
                     '<em>⚠️Если Вам нужно переделать рекламное сообщение, нажмите кнопку <b>Начать заново 🔄</b></em>',
                reply_markup=builder.as_markup(),
            )
            return

        if isinstance(data["adv_pictures"], str):
            await state.update_data(adv_pictures=message.photo[-1].file_id)
        # если отправили более 1 новой картинки, то всё обновилось в AlbumMiddleware

        await completed_adv(message, state, bot)
    else:
        await message.answer(
            text="Я ожидаю от Вас новые картинки\n\n"
                 "Не нужно присылать мне что-то, отличающееся от картинок",
        )


@router.callback_query(StateFilter(AdminAdvSG.adv_change_pics), F.data == "adm_adv_change_pics_cancel")
async def adm_adv_change_pics_cancel_handler(callback: CallbackQuery, state: FSMContext):
    await start_creating_adv(callback, state)
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_change_btn_name")
async def adm_adv_change_btn_name_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Пришлите новое название для кнопки рекламного сообщения!",
    )
    await state.set_state(AdminAdvSG.adv_change_url_btn_name)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_change_url_btn_name))
async def adm_adv_change_btn_name_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        await state.update_data(adv_url_text=message.text)
        await completed_adv(message, state, bot)
    else:
        await message.answer(
            text="Я ожидаю от Вас новое название для кнопки рекламного сообщения!\n\n"
                 "Не нужно присылать мне что-то, отличающееся от текста",
        )


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_adv_change_btn_url")
async def adm_adv_change_btn_url_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Пришлите мне новую ссылку для кнопки рекламного сообщения!",
    )
    await state.set_state(AdminAdvSG.adv_change_url)
    await callback.answer()


@router.message(StateFilter(AdminAdvSG.adv_change_url))
async def adm_adv_change_btn_url_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text:
        await state.update_data(url=message.text)
        await completed_adv(message, state, bot)
    else:
        await message.answer(
            text="Я ожидаю от Вас новую ссылку для кнопки рекламного сообщения!\n\n"
                 "Не нужно присылать мне что-то, отличающееся от текста",
        )
