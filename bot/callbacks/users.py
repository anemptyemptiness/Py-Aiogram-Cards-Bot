from aiogram.filters.callback_data import CallbackData


class UsersCallback(CallbackData, prefix="user"):
    telegram_id: int
    free_cards: int


class PaginationCallbackData(CallbackData, prefix="pag"):
    action: str
    page: int
