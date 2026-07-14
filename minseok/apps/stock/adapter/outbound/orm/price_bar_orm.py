from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class PriceBarOrm(Base):
    __tablename__ = "price_bars"
    __table_args__ = (
        # 멱등 upsert의 축 — 겹침 창 재수집은 여기서 걸러진다
        UniqueConstraint("ticker", "timeframe", "ts", name="uq_price_bars_ticker_timeframe_ts"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(5))  # '5m' | '1d'
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)  # 봉 시작(UTC)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
