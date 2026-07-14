from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class FundamentalSnapshotOrm(Base):
    __tablename__ = "fundamental_snapshots"
    __table_args__ = (
        # 소스(yfinance/dart)별로 같은 날 한 행 — 소스 간 값 대조를 별도 행으로 공존
        UniqueConstraint("ticker", "as_of", "source", name="uq_fundamental_snapshots_ticker_as_of_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    as_of: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(10))  # yfinance | dart
    per: Mapped[float | None] = mapped_column(Float, nullable=True)
    pbr: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe: Mapped[float | None] = mapped_column(Float, nullable=True)
    debt_to_equity: Mapped[float | None] = mapped_column(Float, nullable=True)
    fcf: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    eps: Mapped[float | None] = mapped_column(Float, nullable=True)
    bps: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
