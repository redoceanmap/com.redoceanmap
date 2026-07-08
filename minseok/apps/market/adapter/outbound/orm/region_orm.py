from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class RegionOrm(Base):
    """지역 차원 — 자치구(level1) → 행정동(level2) 자기참조 계층.

    발자국 ERD의 region 패턴(시도→시군구)을 서울 상권의 자치구→행정동에 적용.
    """

    __tablename__ = "region"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    level: Mapped[int] = mapped_column(Integer)  # 1=자치구, 2=행정동
    parent_code: Mapped[str | None] = mapped_column(
        ForeignKey("region.code"), nullable=True, index=True
    )
    x_coord: Mapped[int | None] = mapped_column(Integer, nullable=True)
    y_coord: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_size: Mapped[float | None] = mapped_column(Float, nullable=True)
