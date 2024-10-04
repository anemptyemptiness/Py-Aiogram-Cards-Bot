from math import ceil

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks.users import UsersCallback, PaginationCallbackData
from bot.db.users.requests import UsersDAO
from bot.fsm.fsm import AdminSG, AdminUsersSG
from bot.keyboards.admin_kb import create_admin_kb
from bot.lexicon.lexicon_ru import MONTHS

router = Router(name="premium_router")


async def paginator(session: AsyncSession, page: int = 0):
    builder = InlineKeyboardBuilder()

    users = await UsersDAO.get_users(session=session)

    limit = 8
    start_offset = page * limit
    end_offset = start_offset + limit

    for user in users[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(
            text=f'👤 {user.username if user.username else "user_" + str(user.id)}',
            callback_data=UsersCallback(
                telegram_id=user.telegram_id,
                free_cards=user.free_cards,
            ).pack()
        )
    )

    buttons_row = []

    if page > 0:
        buttons_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=PaginationCallbackData(
                action="prev",
                page=page - 1,
            ).pack())
        )
    if end_offset < len(users):
        buttons_row.append(
            InlineKeyboardButton(text="➡️", callback_data=PaginationCallbackData(
                action="next",
                page=page + 1,
            ).pack())
        )

    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(
        text=f"---{page + 1}/{ceil(len(users) / limit)}---",
        callback_data="number_of_pages",
    ))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))
    return builder.as_markup()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "cancel")
async def go_back_to_adm_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="🔒 Добро пожаловать в админ-панель!",
        reply_markup=create_admin_kb(),
    )
    await state.set_state(AdminSG.in_adm)
    await callback.answer()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "adm_user_back")
async def go_back_to_users_list_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    page = (await state.get_data())["page"]
    count_of_users = len(await UsersDAO.get_users(session=session))
    total_cards = await UsersDAO.get_cards(session=session)

    await callback.message.edit_text(
        text=f"🟢 Активных пользователей: <b>{count_of_users}</b>\n"
             f"💰 Суммарно раскладов: <b>{total_cards}</b>\n\n"
             "👤 Пользователи:",
        reply_markup=await paginator(session=session, page=page)
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "number_of_pages")
async def show_number_of_pages_handler(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(StateFilter(AdminSG.in_adm), F.data == "adm_check_users")
async def adm_check_users_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    count_of_users = len(await UsersDAO.get_users(session=session))
    total_cards = await UsersDAO.get_cards(session=session)

    await callback.message.edit_text(
        text=f"🟢 Активных пользователей: <b>{count_of_users}</b>\n"
             f"💰 Суммарно раскладов: <b>{total_cards}</b>\n\n"
             "👤 Пользователи:",
        reply_markup=await paginator(session=session)
    )
    await state.set_state(AdminUsersSG.check_users)
    await state.update_data(page=0)
    await callback.answer()


@router.callback_query(PaginationCallbackData.filter(), StateFilter(AdminUsersSG.check_users))
async def pagination_handler(
        callback: CallbackQuery, callback_data: PaginationCallbackData, session: AsyncSession, state: FSMContext
):
    count_of_users = len(await UsersDAO.get_users(session=session))
    total_cards = await UsersDAO.get_cards(session=session)

    await callback.message.edit_text(
        text=f"🟢 Активных пользователей: <b>{count_of_users}</b>\n"
             f"💰 Суммарно раскладов: <b>{total_cards}</b>\n\n"
             "👤 Пользователи:",
        reply_markup=await paginator(session=session, page=callback_data.page)
    )
    await state.update_data(page=callback_data.page)
    await callback.answer()


@router.callback_query(UsersCallback.filter(), StateFilter(AdminUsersSG.check_users))
async def user_info_handler(
        callback: CallbackQuery, callback_data: UsersCallback, session: AsyncSession, state: FSMContext
):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="+1 расклад", callback_data="plus_one_free_card"),
        InlineKeyboardButton(text="-1 расклад", callback_data="minus_one_free_card"),
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="adm_user_back"))

    user_info = await UsersDAO.get_user(session=session, telegram_id=callback_data.telegram_id)
    year, month, day = user_info.created_at.strftime("%Y-%m-%d").split("-")

    await state.update_data(
        free_cards=int(user_info.free_cards),
        username=user_info.username,
        created_at=f"{day} {MONTHS[int(month)]} {year}",
        status=user_info.status,
        total_cards=user_info.total_cards,
        telegram_id=callback_data.telegram_id,
    )

    await callback.message.edit_text(
        text=f"👤 Пользователь <b>{user_info.username}</b>\n"
             f"🗓 Зарегистрирован: {day} {MONTHS[int(month)]} {year} год\n\n"
             f"💰 Сделано раскладов: <em>{user_info.total_cards}</em>\n"
             f"🎯 Статус: <em><b>{user_info.status}</b></em>\n"
             f"Количество бесплатных раскладов: <em><b>{user_info.free_cards}</b></em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "plus_one_free_card")
async def plus_one_free_card_handler(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="+1 расклад", callback_data="plus_one_free_card"),
        InlineKeyboardButton(text="-1 расклад", callback_data="minus_one_free_card"),
    )
    builder.row(InlineKeyboardButton(text="Сохранить 💾", callback_data="save_new_free_card_number"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="adm_user_back"))

    data = await state.get_data()

    free_cards = data["free_cards"] + 1
    await state.update_data(free_cards=free_cards)

    await callback.message.edit_text(
        text=f"👤 Пользователь <b>{data['username']}</b>\n"
             f"🗓 Зарегистрирован: {data['created_at']} год\n\n"
             f"💰 Сделано раскладов: <em>{data['total_cards']}</em>\n"
             f"🎯 Статус: <em><b>{data['status']}</b></em>\n"
             f"Количество бесплатных раскладов: <em><b>{free_cards}</b></em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "minus_one_free_card")
async def minus_one_free_card_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data["free_cards"] - 1 < 0:
        await callback.answer(text="Нельзя сделать количество раскладов меньше 0")
    else:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="+1 расклад", callback_data="plus_one_free_card"),
            InlineKeyboardButton(text="-1 расклад", callback_data="minus_one_free_card"),
        )
        builder.row(InlineKeyboardButton(text="Сохранить 💾", callback_data="save_new_free_card_number"))
        builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="adm_user_back"))

        free_cards = data["free_cards"] - 1
        await state.update_data(free_cards=free_cards)

        await callback.message.edit_text(
            text=f"👤 Пользователь <b>{data['username']}</b>\n"
                 f"🗓 Зарегистрирован: {data['created_at']} год\n\n"
                 f"💰 Сделано раскладов: <em>{data['total_cards']}</em>\n"
                 f"🎯 Статус: <em><b>{data['status']}</b></em>\n"
                 f"Количество бесплатных раскладов: <em><b>{free_cards}</b></em>",
            reply_markup=builder.as_markup(),
        )
        await callback.answer()


@router.callback_query(StateFilter(AdminUsersSG.check_users), F.data == "save_new_free_card_number")
async def save_new_free_card_number_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="+1 расклад", callback_data="plus_one_free_card"),
        InlineKeyboardButton(text="-1 расклад", callback_data="minus_one_free_card"),
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="adm_user_back"))

    data = await state.get_data()

    free_cards = data["free_cards"]
    telegram_id = data["telegram_id"]

    await UsersDAO.update_user(session=session, telegram_id=telegram_id, free_cards=free_cards)

    await callback.message.edit_text(
        text=f"👤 Пользователь <b>{data['username']}</b>\n"
             f"🗓 Зарегистрирован: {data['created_at']} год\n\n"
             f"💰 Сделано раскладов: <em>{data['total_cards']}</em>\n"
             f"🎯 Статус: <em><b>{data['status']}</b></em>\n"
             f"Количество бесплатных раскладов: <em><b>{free_cards}</b></em>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()
