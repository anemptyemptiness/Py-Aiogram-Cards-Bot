from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from bot import settings

async_engine = create_async_engine(
    settings.get_database_url,
)

async_session = async_sessionmaker(bind=async_engine)


class Base(DeclarativeBase):
    pass