from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class CommercialChangeBenchmarkOrm(Base):
    """지역(시도) 단위 상권변화 벤치마크 — 분기별 운영/폐업 영업 개월 평균.

    원본 CSV의 서울_운영/폐업_영업_개월_평균은 상권이 아니라 분기+지역에만 종속
    (부분 종속)이라 commercial_change에서 분리. 전국 확장 시 시도별 행이 늘어난다.
    """

    __tablename__ = "commercial_change_benchmark"
    __table_args__ = (
        UniqueConstraint("year_quarter", "region_code", name="uq_commercial_change_benchmark"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    year_quarter: Mapped[int] = mapped_column(Integer, index=True)
    region_code: Mapped[str] = mapped_column(ForeignKey("region.code"), index=True)
    operating_months_avg: Mapped[int] = mapped_column(Integer)
    closure_months_avg: Mapped[int] = mapped_column(Integer)
