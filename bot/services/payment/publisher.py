from nats.js import JetStreamContext


async def payment_publisher(
        js: JetStreamContext,
        subject: str,
        **kwargs,
) -> None:
    await js.publish(subject=subject, headers=kwargs)