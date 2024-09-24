import logging

from aiogram import Bot
from nats.aio.client import Client
from nats.js import JetStreamContext

from bot.services.adv.consumer import AdvConsumer

logger = logging.getLogger(__name__)


async def start_adv_consumer(
        nc: Client,
        js: JetStreamContext,
        bot: Bot,
        subject: str,
        stream: str,
        durable_name: str,
) -> None:
    consumer = AdvConsumer(
        nc=nc,
        js=js,
        bot=bot,
        subject=subject,
        stream=stream,
        durable_name=durable_name,
    )
    logger.info("Start advertisement consumer")
    await consumer.start()