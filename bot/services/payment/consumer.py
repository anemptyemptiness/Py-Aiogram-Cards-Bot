import json

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

from bot.db.base import async_session
from bot.db.buys.requests import BuysDAO
from bot.db.users.requests import UsersDAO


class PaymentConsumer:
    def __init__(
            self,
            nc: Client,
            js: JetStreamContext,
            bot: Bot,
            subject: str,
            stream: str,
            durable_name: str,
    ) -> None:
        self.nc = nc
        self.js = js
        self.bot = bot
        self.subject = subject
        self.stream = stream
        self.durable_name = durable_name

    async def start(self) -> None:
        self.stream_sub = await self.js.subscribe(
            subject=self.subject,
            stream=self.stream,
            cb=self.on_message,
            durable=self.durable_name,
            manual_ack=True,
        )

    async def on_message(self, msg: Msg) -> None:
        user_id = int(msg.headers.get("user_id"))
        total_amount = int(float(msg.headers.get("total_amount")))
        is_success = json.loads(msg.headers.get("is_success"))

        builder = InlineKeyboardBuilder()

        if is_success:
            builder.row(InlineKeyboardButton(text="◀️ В главное меню", callback_data="go_after_payment"))

            async with async_session() as session:
                await BuysDAO.add_buy(
                    session=session,
                    telegram_id=user_id,
                    total_amount=total_amount,
                )
                await UsersDAO.add_buy_by_user(
                    session=session,
                    telegram_id=user_id,
                )

            await self.bot.send_message(
                chat_id=user_id,
                text="Принимаю с Любовью и Благодарностью ❤️\n"
                     "Ваша оплата прошла <b>успешно</b> ✅",
                reply_markup=builder.as_markup(),
            )
        else:
            builder.row(InlineKeyboardButton(text="◀️ В главное меню", callback_data="go_to_menu"))

            await self.bot.send_message(
                chat_id=user_id,
                text="К сожалению, оплата прошла <b>неуспешно</b> ❌",
                reply_markup=builder.as_markup(),
            )
        await msg.ack()
