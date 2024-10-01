import asyncio
import json
from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

from bot.db.base import async_session
from bot.db.users.requests import UsersDAO


class AdvConsumer:
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
        dt_send = msg.headers.get("dt_send")
        dt_send = datetime.strptime(dt_send, "%Y-%m-%d %H:%M").replace(tzinfo=timezone(timedelta(hours=3)))
        dt_now = datetime.now(tz=timezone(timedelta(hours=3)))

        if dt_send > dt_now:
            delay = (dt_send - dt_now).total_seconds()
            await msg.nak(delay=delay)
        else:
            text = json.loads(msg.headers.get("text"))
            pictures = json.loads(msg.headers.get("pictures"))
            url = json.loads(msg.headers.get("url"))
            url_text = json.loads(msg.headers.get("url_text"))

            builder = InlineKeyboardBuilder()

            async with async_session() as session:
                active_users = await UsersDAO.get_users(session=session, is_active=True, status="normal")

            if url:
                builder.row(InlineKeyboardButton(text=url_text, url=url))

            if isinstance(pictures, list):
                pictures_media = [
                    InputMediaPhoto(
                        media=photo_file_id,
                        caption=f"{text}" if not i else "",
                    ) for i, photo_file_id in enumerate(pictures)
                ]
                for user in active_users:
                    try:
                        await self.bot.send_media_group(
                            chat_id=user.telegram_id,
                            media=pictures_media,
                        )
                        await asyncio.sleep(1)
                    except Exception:
                        pass
            elif isinstance(pictures, str):
                for user in active_users:
                    try:
                        await self.bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=pictures,
                            caption=text,
                            reply_markup=builder.as_markup(),
                        )
                        await asyncio.sleep(1)
                    except Exception:
                        pass
            else:
                for user in active_users:
                    try:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=text,
                            reply_markup=builder.as_markup(),
                        )
                        await asyncio.sleep(1)
                    except Exception:
                        pass
            await msg.ack()
