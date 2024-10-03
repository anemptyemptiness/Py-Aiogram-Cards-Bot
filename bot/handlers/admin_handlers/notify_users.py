import json
from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from nats.js import JetStreamContext

from bot.callbacks.calendar import MonthToCallbackData, YearToCallbackData, DayToCallbackData, HourToCallbackData
from bot.config import settings
from bot.fsm.fsm import AdminSG, AdminNotifyUsersSG
from bot.handlers.admin_handlers.utils import get_month_kb, get_year_kb, get_day_kb
from bot.keyboards.admin_kb import create_admin_kb
from bot.lexicon.lexicon_ru import MONTHS, MONTH_DAYS
from bot.services.notify_users.publisher import notify_users_publisher

router = Router(name="adm_notify_users_router")


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), F.data == "cancel")
async def go_back_to_adm_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await state.set_state(AdminSG.in_adm)
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_notify")
async def adm_notify_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>год</b> даты, <b>когда мы уведомим пользователей</b>",
        reply_markup=get_year_kb(builder=builder, cb_data=YearToCallbackData),
    )
    await state.set_state(AdminNotifyUsersSG.notify_date)


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), F.data == "adm_notify")
async def adm_notify_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>год</b> даты, <b>когда мы уведомим пользователей</b>",
        reply_markup=get_year_kb(builder=builder, cb_data=YearToCallbackData),
    )
    await state.set_state(AdminNotifyUsersSG.notify_date)


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), YearToCallbackData.filter())
async def select_year_to_notify_handler(
        callback: CallbackQuery,
        callback_data: YearToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(year_to=callback_data.year_to)

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>месяц</b> даты, <b>когда мы уведомим пользователей</b>",
        reply_markup=get_month_kb(builder=builder, cb_data=MonthToCallbackData, date_data=await state.get_data()),
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), MonthToCallbackData.filter())
async def select_month_to_notify_handler(
        callback: CallbackQuery,
        callback_data: MonthToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(month_to=callback_data.month_to)

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>день</b>, <b>когда мы уведомим пользователей</b>",
        reply_markup=get_day_kb(builder=builder, cb_data=DayToCallbackData, date_data=await state.get_data()),
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), DayToCallbackData.filter())
async def select_day_to_notify_handler(
        callback: CallbackQuery,
        callback_data: DayToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(day_to=callback_data.day_to)
    dt_now = datetime.now(tz=timezone(timedelta(hours=3)))
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    buttons = list()

    if data["year_to"] == dt_now.year and data["month_to"] == dt_now.month and data["day_to"] == dt_now.day:
        if dt_now.month == 12 and dt_now.day == 31 and dt_now.hour == 23:
            # случай, если будут настраивать отправку
            # сообщения в 23 часа 31 декабря
            await state.update_data(year_to=data['year_to'] + 1, month_to=1, day_to=1)
            start_hour = 0
        elif MONTH_DAYS[dt_now.month] == data['day_to'] and dt_now.hour == 23:
            # случай, если выбрали последний день какого-то месяца
            await state.update_data(month=data['month_to'] + 1, day_to=1)
            start_hour = 0
        elif dt_now.hour == 23:
            # случай, если уже 23 часа
            await state.update_data(day_to=data['day_to'] + 1)
            start_hour = 0
        else:
            start_hour = dt_now.hour + 1
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
        text="Выберите <b>час</b>, <b>в который мы уведомим пользователей</b>",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), HourToCallbackData.filter())
async def select_hour_to_notify_handler(
        callback: CallbackQuery,
        callback_data: HourToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(hour_to=callback_data.hour_to)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Всё верно ✅", callback_data="adm_date_notify_correct"))
    builder.row(InlineKeyboardButton(text="Начать заново 🔄", callback_data="adm_notify"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text=f"Уведомим пользователей <b>{data['day_to']} {MONTHS[data['month_to']]} {data['year_to']} года "
             f"в {data['hour_to']}:00</b>\n\n"
             "Всё ли верно?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_date), F.data == "adm_date_notify_correct")
async def adm_notify_correct_date_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="Пришлите мне сообщение, которое надо будет отправить пользователям"
    )
    await state.set_state(AdminNotifyUsersSG.notify_text)


@router.message(StateFilter(AdminNotifyUsersSG.notify_text), F.text)
async def adm_notify_text_handler(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Всё верно ✅", callback_data="adm_text_notify_correct"))
    builder.row(InlineKeyboardButton(text="Новый текст 🔄", callback_data="adm_text_notify_change"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await state.update_data(text=message.text)
    data = await state.get_data()

    await message.answer(
        text=f"Уведомим пользователей <b>{data['day_to']} {MONTHS[data['month_to']]} {data['year_to']} года "
             f"в {data['hour_to']}:00</b>\n\n"
             "Текст сообщения:\n"
             f"<em>{data['text']}</em>\n\n"
             "Всё ли верно?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_text), F.data == "adm_text_notify_change")
async def adm_notify_text_change_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Пришлите мне сообщение, которое надо будет отправить пользователям"
    )


@router.callback_query(StateFilter(AdminNotifyUsersSG.notify_text), F.data == "adm_text_notify_correct")
async def adm_notify_text_correct_handler(callback: CallbackQuery, js: JetStreamContext, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    dt_send = datetime(
        year=data['year_to'],
        month=data['month_to'],
        day=data['day_to'],
        hour=data['hour_to'],
        minute=0,
        tzinfo=timezone(timedelta(hours=3)),
    )
    await notify_users_publisher(
        js=js,
        subject=settings.NATS_CONSUMER_SUBJECT_NOTIFY_USERS,
        dt_send=dt_send.strftime("%Y-%m-%d %H:%M"),
        text=json.dumps(data['text']),
    )
    await callback.message.edit_text(
        text=f"✅ Отложенное сообщение запланировано на {dt_send.strftime('%Y-%m-%d %H:%M')}\n\n"
             "🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await state.set_state(AdminSG.in_adm)
