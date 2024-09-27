import logging

import nats
from nats.aio.client import Client
from nats.js import JetStreamContext
from nats.js.api import (
    StreamConfig,
    RetentionPolicy,
    StorageType,
    DiscardPolicy,
)

from bot.config import settings

logger = logging.getLogger(__name__)


async def connect_to_nats(servers: str | list[str]) -> tuple[Client, JetStreamContext]:
    nc: Client = await nats.connect(servers=servers)
    js: JetStreamContext = nc.jetstream()

    stream_config_adv = StreamConfig(
        name=settings.NATS_STREAM_ADV,
        subjects=[settings.NATS_CONSUMER_SUBJECT_ADV],
        retention=RetentionPolicy.INTEREST,
        discard=DiscardPolicy.OLD,
        storage=StorageType.FILE,
        allow_rollup_hdrs=True,
    )
    stream_config_payment = StreamConfig(
        name=settings.NATS_STREAM_PAYMENT,
        subjects=[settings.NATS_CONSUMER_SUBJECT_PAYMENT],
        retention=RetentionPolicy.INTEREST,
        discard=DiscardPolicy.OLD,
        storage=StorageType.FILE,
        allow_rollup_hdrs=True,
    )

    await js.add_stream(stream_config_adv)
    await js.add_stream(stream_config_payment)

    logger.info("Successfully connect to NATS server!")

    return nc, js
