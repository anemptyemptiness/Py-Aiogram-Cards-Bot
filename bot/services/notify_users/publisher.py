from nats.js import JetStreamContext


async def notify_users_publisher(
        js: JetStreamContext,
        subject: str,
        **kwargs,
) -> None:
    await js.publish(subject=subject, headers=kwargs)