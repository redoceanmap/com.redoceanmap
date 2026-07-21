from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class StockDemandOrm(Base):
    """분석 질문 수요 — 어떤 티커가 얼마나 자주 요청되는지. 워치리스트 수요 편입의 재료."""

    __tablename__ = "stock_demand"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    ask_count: Mapped[int] = mapped_column(Integer, default=1)
    last_asked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
