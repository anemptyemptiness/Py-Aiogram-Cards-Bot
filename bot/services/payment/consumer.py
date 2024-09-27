from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

from bot.db.base import async_session
from bot.db.buys.requests import BuysDAO


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

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Продолжить ➡️", callback_data="go_after_payment"))

        async with async_session() as session:
            await BuysDAO.add_buy(
                session=session,
                telegram_id=user_id,
                total_amount=total_amount,
            )

        await self.bot.send_message(
            chat_id=user_id,
            text="Ваша оплата прошла <b>успешно</b> ✅",
            reply_markup=builder.as_markup(),
        )
        await msg.ack()
