from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import MenuSG, AdminSG
from bot.keyboards.admin_kb import create_admin_kb

router = Router(name="admin_startup_router")


@router.message(Command(commands="admin"))
async def admin_command(message: Message, state: FSMContext, session: AsyncSession):
    user = await UsersDAO.get_user(session=session, telegram_id=message.from_user.id)

    if user.status == "admin":
        if await state.get_state() != MenuSG.in_menu:
            await message.answer(
                text="Вероятнее всего, Вы находитесь в одном из методов расклада карт!\n\n"
                     "Пожалуйста, завершите метод расклада и попробуйте заново "
                     "написать команду /admin <b>из главного меню</b>",
            )
        else:
            await message.answer(
                text="🔒 Добро пожаловать в админ-панель!",
                reply_markup=create_admin_kb(),
            )
            await state.clear()
            await state.set_state(AdminSG.in_adm)