import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Ticker(Base):
    __tablename__ = "tickers"

    symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    sector: Mapped[str] = mapped_column(String(100))

    prices: Mapped[list["DailyPrice"]] = relationship(back_populates="ticker")


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("ticker_symbol", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("tickers.symbol"))
    date: Mapped[datetime.date] = mapped_column(Date)
    close: Mapped[float] = mapped_column(Numeric(12, 4))
    volume: Mapped[int]

    ticker: Mapped["Ticker"] = relationship(back_populates="prices")


class Snapshot(Base):
    __tablename__ = "snapshots"

    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    computed_at: Mapped[datetime.datetime] = mapped_column(DateTime)


class Move(Base):
    __tablename__ = "moves"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_date: Mapped[datetime.date] = mapped_column(ForeignKey("snapshots.date"))
    ticker_symbol: Mapped[str] = mapped_column(ForeignKey("tickers.symbol"))
    move_type: Mapped[str] = mapped_column(String(20))
    value: Mapped[float] = mapped_column(Numeric(12, 4))
