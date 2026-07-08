from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ServiceCategoryOrm(Base):
    """서비스 업종 차원 — 서비스_업종_코드(예: CS100010) → 업종명. 평면(계층 없음)."""

    __tablename__ = "service_category"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
