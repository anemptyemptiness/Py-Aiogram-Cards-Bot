from aiogram import Router
from aiogram.types import CallbackQuery, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.users.requests import UsersDAO

router = Router(name="utils_router")


@router.callback_query()
async def default_callback_handler(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.answer()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def kicked_handler(event: ChatMemberUpdated, session: AsyncSession):
    await UsersDAO.update_user(
        session=session,
        telegram_id=event.from_user.id,
        is_active=False,
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def member_handler(event: ChatMemberUpdated, session: AsyncSession):
    await UsersDAO.update_user(
        session=session,
        telegram_id=event.from_user.id,
        is_active=True,
    )
