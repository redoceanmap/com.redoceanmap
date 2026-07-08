from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class TradeAreaDivisionOrm(Base):
    """상권 구분 차원 — A(골목상권)/D(발달상권)/R(전통시장)/U(관광특구) 소차원."""

    __tablename__ = "trade_area_division"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
