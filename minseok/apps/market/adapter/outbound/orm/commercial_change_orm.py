from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from market.adapter.outbound.orm.base_orm import MarketStatMixin


class CommercialChangeOrm(MarketStatMixin, Base):
    __tablename__ = "commercial_change"
    __table_args__ = (
        UniqueConstraint("year_quarter", "trdar_code", name="uq_commercial_change"),
    )

    change_indicator: Mapped[str] = mapped_column(ForeignKey("change_indicator.code"))
    operating_months_avg: Mapped[int] = mapped_column(Integer)
    closure_months_avg: Mapped[int] = mapped_column(Integer)
