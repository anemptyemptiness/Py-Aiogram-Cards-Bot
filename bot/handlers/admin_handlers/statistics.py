from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks.calendar import (
    MonthFromCallbackData,
    DayFromCallbackData,
    MonthToCallbackData,
    DayToCallbackData,
    YearFromCallbackData,
    YearToCallbackData,
)
from bot.db.buys.requests import BuysDAO
from bot.fsm.fsm import AdminSG, AdminStatisticsSG
from bot.handlers.admin_handlers.utils import get_year_kb
from bot.keyboards.admin_kb import create_admin_kb
from bot.lexicon.lexicon_ru import MONTHS, MONTH_DAYS

router = Router(name="statistics_router")


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "cancel")
async def go_back_to_adm_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await state.set_state(AdminSG.in_adm)
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_per_day_nothing")
async def adm_stats_per_day_nothing_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_per_month_nothing")
async def adm_stats_per_month_nothing_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_by_hand_nothing")
async def adm_stats_by_hand_nothing_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_stats")
async def adm_stats_handler(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="За день", callback_data="adm_stats_per_day"),
        InlineKeyboardButton(text="За месяц", callback_data="adm_stats_per_month"),
    )
    builder.row(InlineKeyboardButton(text="Задать дату вручную", callback_data="adm_stats_by_hand"))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    await callback.message.edit_text(
        text="Выберите статистику:",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AdminStatisticsSG.stats)
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_per_day")
async def adm_stats_per_day_handler(callback: CallbackQuery, session: AsyncSession):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="За день ✅", callback_data="adm_stats_per_day_nothing"),
        InlineKeyboardButton(text="За месяц", callback_data="adm_stats_per_month"),
    )
    builder.row(InlineKeyboardButton(text="Задать дату вручную", callback_data="adm_stats_by_hand"))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    date_now = datetime.now(tz=timezone(timedelta(hours=3)))
    count_of_buys = await BuysDAO.get_buys_per_single_date(session=session, date_of_buy=date_now.date())
    total_amount = await BuysDAO.get_total_amount_per_single_date(session=session, date_of_buy=date_now.date())

    await callback.message.edit_text(
        text=f"📊 Статистика за {date_now.date()}\n\n"
             f"📝 Покупок за сегодня: <em>{count_of_buys}</em>\n"
             f"💰 Сумма продаж за сегодня: <em>{str(total_amount) + '₽' if total_amount else 'Нет продаж ❌'}</em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_per_month")
async def adm_stats_per_month_handler(callback: CallbackQuery, session: AsyncSession):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="За день", callback_data="adm_stats_per_day"),
        InlineKeyboardButton(text="За месяц ✅", callback_data="adm_stats_per_month_nothing"),
    )
    builder.row(InlineKeyboardButton(text="Задать дату вручную", callback_data="adm_stats_by_hand"))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    date_now = datetime.now(tz=timezone(timedelta(hours=3)))
    start_month_date = date_now.replace(day=1, hour=0, minute=0, second=0)

    count_of_buys = await BuysDAO.get_buys_interval(
        session=session,
        date_from=start_month_date.date(),
        date_to=date_now.date(),
    )
    total_amount = await BuysDAO.get_total_amount_interval(
        session=session,
        date_from=start_month_date.date(),
        date_to=date_now.date(),
    )

    await callback.message.edit_text(
        text=f"📊 Статистика от {start_month_date.date()} до {date_now.date()}\n\n"
             f"📝 Покупок за текущий месяц: <em>{count_of_buys}</em>\n"
             f"💰 Сумма продаж за текущий месяц: <em>{str(total_amount) + ' ₽' if total_amount else 'Нет продаж ❌'}</em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_stats_by_hand")
async def adm_stats_by_hand_handler(callback: CallbackQuery):
    await callback.answer()

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>год</b>, <b>от которого</b> будем собирать информацию",
        reply_markup=get_year_kb(builder=builder, cb_data=YearFromCallbackData),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), YearFromCallbackData.filter())
async def adm_stats_by_hand_year_from_handler(
        callback: CallbackQuery,
        callback_data: YearFromCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(year_from=callback_data.year_from)

    builder = InlineKeyboardBuilder()
    buttons = list()

    for month in range(1, 12 + 1):
        buttons.append(
            InlineKeyboardButton(
                text=f"{MONTHS[month]}",
                callback_data=MonthFromCallbackData(
                    month_from=month,
                ).pack(),
            )
        )
    builder.row(*buttons, width=3)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text="Выберите месяц даты, <b>от которой</b> будем собирать информацию",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), MonthFromCallbackData.filter())
async def adm_stats_by_hand_month_from_handler(
        callback: CallbackQuery, callback_data: MonthFromCallbackData, state: FSMContext
):
    await callback.answer()
    await state.update_data(month_from=callback_data.month_from)
    builder = InlineKeyboardBuilder()

    for day in range(1, MONTH_DAYS[callback_data.month_from] + 1):
        builder.add(
            InlineKeyboardButton(
                text=f"{day}",
                callback_data=DayFromCallbackData(
                    day_from=day,
                ).pack()
            )
        )
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    await callback.message.edit_text(
        text="Выберите день <b>выбранного на предыдущем шаге</b> месяца",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), DayFromCallbackData.filter())
async def adm_stats_by_hand_day_from_handler(
        callback: CallbackQuery,
        callback_data: DayFromCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(day_from=callback_data.day_from)

    builder = InlineKeyboardBuilder()

    await callback.message.edit_text(
        text="Выберите <b>год</b>, <b>до которого</b> будем собирать информацию",
        reply_markup=get_year_kb(builder=builder, cb_data=YearToCallbackData),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), YearToCallbackData.filter())
async def adm_stats_by_hand_year_to_handler(
        callback: CallbackQuery,
        callback_data: YearToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(year_to=callback_data.year_to)

    builder = InlineKeyboardBuilder()
    buttons = list()

    for month in range(1, 12 + 1):
        buttons.append(
            InlineKeyboardButton(
                text=f"{MONTHS[month]}",
                callback_data=MonthToCallbackData(
                    month_to=month,
                ).pack(),
            )
        )
    builder.row(*buttons, width=3)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))

    await callback.message.edit_text(
        text="Выберите месяц даты, <b>до которой</b> будем собирать информацию",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), MonthToCallbackData.filter())
async def adm_stats_by_hand_month_to_handler(
        callback: CallbackQuery,
        callback_data: MonthToCallbackData,
        state: FSMContext,
):
    await callback.answer()
    await state.update_data(month_to=callback_data.month_to)

    builder = InlineKeyboardBuilder()

    for day in range(1, MONTH_DAYS[callback_data.month_to] + 1):
        builder.add(
            InlineKeyboardButton(
                text=f"{day}",
                callback_data=DayToCallbackData(
                    day_to=day,
                ).pack()
            )
        )
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    await callback.message.edit_text(
        text="Выберите день <b>выбранного на предыдущем шаге</b> месяца",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(StateFilter(AdminStatisticsSG.stats), DayToCallbackData.filter())
async def adm_stats_by_hand_day_to_handler(
        callback: CallbackQuery, callback_data: DayToCallbackData, state: FSMContext
):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Всё верно ✅", callback_data="adm_date_by_hand_correct"))
    builder.row(InlineKeyboardButton(text="Начать заново 🔄", callback_data="adm_stats_by_hand"))

    await state.update_data(day_to=callback_data.day_to)
    data = await state.get_data()

    await callback.message.edit_text(
        text="Вы выбрали следующие даты\n\n"
             f"От: <b>{data['day_from']} {MONTHS[data['month_from']]} {data['year_from']} год</b>\n"
             f"До: <b>{data['day_to']} {MONTHS[data['month_to']]} {data['year_to']} год</b>\n\n"
             "Всё ли верно?",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminStatisticsSG.stats), F.data == "adm_date_by_hand_correct")
async def adm_stats_by_hand_correct_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="За день", callback_data="adm_stats_per_day"),
        InlineKeyboardButton(text="За месяц", callback_data="adm_stats_per_month"),
    )
    builder.row(InlineKeyboardButton(text="Задать дату вручную ✅", callback_data="adm_stats_by_hand_nothing"))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))

    data = await state.get_data()
    date_from = datetime(
        year=data["year_from"],
        month=data["month_from"],
        day=data["day_from"],
        hour=0, minute=0, second=0,
        tzinfo=timezone(timedelta(hours=3)),
    )
    date_to = datetime(
        year=data["year_to"],
        month=data["month_to"],
        day=data["day_to"],
        hour=23, minute=59, second=59,
        tzinfo=timezone(timedelta(hours=3)),
    )

    count_of_buys = await BuysDAO.get_buys_interval(
        session=session,
        date_from=date_from.date(),
        date_to=date_to.date(),
    )
    total_amount = await BuysDAO.get_total_amount_interval(
        session=session,
        date_from=date_from.date(),
        date_to=date_to.date(),
    )

    await callback.message.edit_text(
        text=f"📊 Статистика от {date_from.date()} до {date_to.date()}\n\n"
             f"📝 Покупок за период: <em>{count_of_buys}</em>\n"
             f"💰 Сумма продаж за период: <em>{str(total_amount) + '₽' if total_amount else 'Нет продаж ❌'}</em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
