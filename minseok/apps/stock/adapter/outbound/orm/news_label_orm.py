from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class NewsLabelOrm(Base):
    __tablename__ = "news_labels"
    __table_args__ = (
        # 라벨러 버전별로 같은 뉴스에 한 행 — 상위 모델 재라벨링은 별도 행으로 공존
        UniqueConstraint("news_id", "labeler", name="uq_news_labels_news_id_labeler"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news_articles.id", ondelete="CASCADE"), index=True
    )
    labeler: Mapped[str] = mapped_column(String(40))  # 예: exaone-2.4b-awq
    sentiment: Mapped[float] = mapped_column(Float)  # -1.0 ~ +1.0
    event_type: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float)  # 0.0 ~ 1.0
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
