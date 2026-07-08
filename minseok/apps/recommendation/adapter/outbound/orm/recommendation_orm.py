from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class RecommendationOrm(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    trdar_code: Mapped[int] = mapped_column(Integer, index=True)
    trdar_name: Mapped[str] = mapped_column(String(100))
    district_name: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(100))
    reason: Mapped[str] = mapped_column(Text)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
