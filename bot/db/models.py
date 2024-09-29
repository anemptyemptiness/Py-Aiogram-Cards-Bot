from datetime import datetime, timezone, timedelta

from sqlalchemy.dialects.postgresql import BIGINT, DATE, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from bot.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT)
    status: Mapped[str] = mapped_column(default="normal")
    username: Mapped[str] = mapped_column(nullable=True)
    free_cards: Mapped[int] = mapped_column(default=3)
    created_at: Mapped[datetime] = mapped_column(
        DATE(),
        default=datetime.now(tz=timezone(timedelta(hours=3))),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    buys: Mapped["Buys"] = relationship(back_populates="user", uselist=False)


class Buys(Base):
    __tablename__ = "buys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="NO ACTION"))
    total_amount: Mapped[int] = mapped_column(default=0)
    buy_datetime: Mapped[datetime] = mapped_column(
        DATE(),
        default=datetime.now(tz=timezone(timedelta(hours=3))).date(),
    )

    user: Mapped["User"] = relationship(back_populates="buys", uselist=False)


class Invoices(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DATE(),
        default=datetime.now(tz=timezone(timedelta(hours=3))),
        server_default=func.now(),
    )
