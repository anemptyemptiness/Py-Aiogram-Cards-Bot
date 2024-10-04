from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User


class UsersDAO:
    @classmethod
    async def add_user(
            cls,
            session: AsyncSession,
            telegram_id: int,
            username: str,
    ):
        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
            )
        )

        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_user(
            cls,
            session: AsyncSession,
            telegram_id: int,
    ):
        query = (
            select(User)
            .where(User.telegram_id == telegram_id)
        )

        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def get_users(
            cls,
            session: AsyncSession,
            **kwargs,
    ):
        query = select(User).filter_by(**kwargs).order_by(User.id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update_user(
            cls,
            session: AsyncSession,
            telegram_id: int,
            **kwargs,
    ):
        stmt = (
            update(User)
            .values(**kwargs)
            .where(User.telegram_id == telegram_id)
        )
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def add_buy_by_user(
            cls,
            session: AsyncSession,
            telegram_id: int,
    ):
        total_cards = select(User.total_cards).where(User.telegram_id == telegram_id).scalar_subquery()
        stmt = update(User).values(total_cards=total_cards + 1)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_cards(
            cls,
            session: AsyncSession,
    ):
        query = select(func.sum(User.total_cards))
        result = await session.execute(query)
        return result.scalar()
