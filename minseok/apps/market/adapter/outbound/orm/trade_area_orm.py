from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from market.utils.coords import tm_to_wgs84


class TradeAreaOrm(Base):
    """상권 차원 — 중심 차원. 팩트들이 code(상권_코드)로 참조한다.

    구분(division)·지역(region=행정동)은 별도 차원으로 정규화 참조.
    """

    __tablename__ = "trade_area"

    code: Mapped[int] = mapped_column(Integer, primary_key=True)  # 상권_코드
    name: Mapped[str] = mapped_column(String(100))
    division_code: Mapped[str] = mapped_column(
        ForeignKey("trade_area_division.code"), index=True
    )
    region_code: Mapped[str | None] = mapped_column(
        ForeignKey("region.code"), nullable=True, index=True
    )  # 행정동 코드
    x_coord: Mapped[int] = mapped_column(Integer)
    y_coord: Mapped[int] = mapped_column(Integer)
    area_size: Mapped[float | None] = mapped_column(Float, nullable=True)

    @property
    def lat(self) -> float:
        return tm_to_wgs84(self.x_coord, self.y_coord)[0]

    @property
    def lng(self) -> float:
        return tm_to_wgs84(self.x_coord, self.y_coord)[1]
