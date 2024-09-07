from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def connection_test(session: AsyncSession):
    stmt = select(1)
    return await session.scalar(stmt)