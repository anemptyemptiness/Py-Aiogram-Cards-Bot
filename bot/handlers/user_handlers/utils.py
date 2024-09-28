from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.users.requests import UsersDAO
from bot.keyboards.user_kb import create_menu_kb

router = Router(name="utils_router")


@router.callback_query(F.data == "go_after_payment")
async def go_after_payment_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()

    await callback.message.answer(
        text="Вы находитесь в главном меню 🏡",
        reply_markup=create_menu_kb(),
    )
    await state.clear()


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
