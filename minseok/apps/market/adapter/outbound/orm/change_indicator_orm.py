from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ChangeIndicatorOrm(Base):
    """상권 변화 지표 차원 — 지표 코드(HH/HL/LH/LL 등) → 지표명 소차원."""

    __tablename__ = "change_indicator"

    code: Mapped[str] = mapped_column(String(4), primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
