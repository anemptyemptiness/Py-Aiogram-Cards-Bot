from datetime import datetime, date

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Buys, User


class BuysDAO:
    @classmethod
    async def get_buys_per_single_date(
            cls,
            session: AsyncSession,
            date_of_buy: date,
    ):
        query = (
            select(func.count("*"))
            .select_from(Buys)
            .where(Buys.buy_datetime == date_of_buy)
        )

        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def get_total_amount_per_single_date(
            cls,
            session: AsyncSession,
            date_of_buy: date,
    ):
        query = (
            select(func.sum(Buys.total_amount))
            .select_from(Buys)
            .where(Buys.buy_datetime == date_of_buy)
        )

        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def get_buys_interval(
            cls,
            session: AsyncSession,
            date_from: date,
            date_to: date,
    ):
        query = (
            select(func.count("*"))
            .select_from(Buys)
            .where(
                Buys.buy_datetime.between(
                    date_from,
                    date_to,
                )
            )
        )

        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def get_total_amount_interval(
            cls,
            session: AsyncSession,
            date_from: date,
            date_to: date,
    ):
        query = (
            select(func.sum(Buys.total_amount))
            .select_from(Buys)
            .where(
                Buys.buy_datetime.between(
                    date_from,
                    date_to,
                )
            )
        )

        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def add_buy(
            cls,
            session: AsyncSession,
            telegram_id: int,
            total_amount: int,
    ):
        stmt = (
            insert(Buys)
            .values(
                total_amount=total_amount,
                user_id=select(User.id).where(User.telegram_id == telegram_id).scalar_subquery(),
            )
        )

        await session.execute(stmt)
        await session.commit()
