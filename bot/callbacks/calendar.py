from aiogram.filters.callback_data import CallbackData


class MonthFromCallbackData(CallbackData, prefix="month_from"):
    month_from: int


class DayFromCallbackData(CallbackData, prefix="day_from"):
    day_from: int


class MonthToCallbackData(CallbackData, prefix="month_to"):
    month_to: int


class DayToCallbackData(CallbackData, prefix="day_to"):
    day_to: int


class HourToCallbackData(CallbackData, prefix="hour_to"):
    hour_to: int


class MinuteToCallbackData(CallbackData, prefix="min_to"):
    minute_to: int
