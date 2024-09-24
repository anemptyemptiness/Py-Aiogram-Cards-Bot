import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import settings, redis
from bot.db.requests import connection_test
from bot.handlers import (
    startup_router,
    mini_dialog_router,
    menu_router,
    crystal_per_day_router,
    crystal_3_router,
    crystal_5_router,
    crystal_question_router,
    utils_router,
    admin_startup_router,
    premium_router,
    statistics_router,
    adv_router,
)
from bot.middlewares.album import AlbumMiddleware
from bot.middlewares.db import DbSessionMiddleware
from bot.menu_commands import set_default_commands
from bot.utils.connect_to_nats import connect_to_nats
from bot.utils.start_consumers import start_adv_consumer


async def main():
    logging.basicConfig(
        format='[{asctime}] #{levelname:8} {filename}: '
               '{lineno} - {name} - {message}',
        style="{",
        level=logging.INFO,
    )

    bot = Bot(
        token=settings.TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )
    async_engine = create_async_engine(settings.get_database_url)
    sessionmaker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    async with sessionmaker() as session:
        await connection_test(session)

    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )

    dp = Dispatcher(storage=storage)
    dp.update.middleware(middleware=DbSessionMiddleware(session_pool=sessionmaker))

    dp.include_routers(
        startup_router,
        mini_dialog_router,
        menu_router,
        crystal_per_day_router,
        crystal_3_router,
        crystal_5_router,
        crystal_question_router,
        admin_startup_router,
        premium_router,
        statistics_router,
        adv_router,
        utils_router,
    )
    adv_router.message.middleware(middleware=AlbumMiddleware(wait_time_seconds=2))

    nc, js = await connect_to_nats(servers=settings.NATS_HOST)

    await set_default_commands(bot=bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await asyncio.gather(
            dp.start_polling(
                bot,
                js=js,
                consumer=settings.NATS_CONSUMER_SUBJECT,
            ),
            start_adv_consumer(
                nc=nc,
                js=js,
                bot=bot,
                subject=settings.NATS_CONSUMER_SUBJECT,
                stream=settings.NATS_STREAM,
                durable_name=settings.NATS_DURABLE_NAME,
            )
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await nc.close()
        logger.info("Connection to NATS closed")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt):
        logger.info("Bot stopped")