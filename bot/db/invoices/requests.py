from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from bot.db.models import Invoices


class InvoicesDAO:
    @classmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
    ):
        stmt = insert(Invoices).returning(Invoices.id)
        invoice_id = await session.execute(stmt)
        await session.commit()

        return invoice_id.scalar()
