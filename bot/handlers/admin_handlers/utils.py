from datetime import datetime, timezone, timedelta

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.calendar import MonthFromCallbackData, DayFromCallbackData, YearFromCallbackData
from bot.lexicon.lexicon_ru import MONTHS, MONTH_DAYS


def get_year_kb(
        builder: InlineKeyboardBuilder,
        cb_data
):
    buttons = list()
    current_year = datetime.now(tz=timezone(timedelta(hours=3))).year

    for year in range(current_year, current_year + 2):
        if cb_data is YearFromCallbackData:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{year}",
                    callback_data=cb_data(
                        year_from=year,
                    ).pack(),
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{year}",
                    callback_data=cb_data(
                        year_to=year,
                    ).pack(),
                )
            )
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))
    return builder.as_markup()


def get_month_kb(
        builder: InlineKeyboardBuilder,
        date_data: dict,
        cb_data
):
    dt_now = datetime.now(tz=timezone(timedelta(hours=3)))
    buttons = list()

    if cb_data is MonthFromCallbackData:
        year = date_data.get("year_from")
    else:
        year = date_data.get("year_to")

    if year == dt_now.year:
        start_month = dt_now.month
    else:
        start_month = 1

    for month in range(start_month, 12 + 1):
        if cb_data is MonthFromCallbackData:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{MONTHS[month]}",
                    callback_data=cb_data(
                        month_from=month,
                    ).pack(),
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=f"{MONTHS[month]}",
                    callback_data=cb_data(
                        month_to=month,
                    ).pack(),
                )
            )
    builder.row(*buttons, width=3)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel"))
    return builder.as_markup()


def get_day_kb(
        builder: InlineKeyboardBuilder,
        date_data: dict,
        cb_data
):
    month = date_data.get("month_from", None)

    if date_data.get("month_to", None):
        month = date_data["month_to"]

    for day in range(1, MONTH_DAYS[month] + 1):
        if cb_data is DayFromCallbackData:
            builder.add(
                InlineKeyboardButton(
                    text=f"{day}",
                    callback_data=cb_data(
                        day_from=day,
                    ).pack()
                )
            )
        else:
            builder.add(
                InlineKeyboardButton(
                    text=f"{day}",
                    callback_data=cb_data(
                        day_to=day,
                    ).pack()
                )
            )
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))
    return builder.as_markup()