from aiogram import Router
from aiogram.types import CallbackQuery

router = Router(name="utils_router")


@router.callback_query()
async def default_callback_handler(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.answer()
