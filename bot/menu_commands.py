from aiogram import Bot
from aiogram import types


async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Главное меню 🏡"),
        types.BotCommand(command="consultation", description="Индивидуальная консультация 📝"),
        types.BotCommand(command="support", description="Тех. поддержка ⚒"),
        types.BotCommand(command="site", description="Сайт основателя техники 🔗"),
        types.BotCommand(command="rules", description="Правила оформления заказа 📝"),
        types.BotCommand(command="oferta", description="Оферта 📜"),
    ])