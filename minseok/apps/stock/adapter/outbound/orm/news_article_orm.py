from datetime import datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class NewsArticleOrm(Base):
    __tablename__ = "news_articles"
    __table_args__ = (
        # 같은 기사(url)라도 종목별 관련성은 별개 샘플 — 학습 조인 키(ticker) 단위로 유니크
        UniqueConstraint("url", "ticker", name="uq_news_articles_url_ticker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)  # 원문 그대로 — 가공(접두·번역·요약) 저장 금지
    source: Mapped[str] = mapped_column(String(100), default="")
    url: Mapped[str] = mapped_column(String(1000))
    ticker: Mapped[str] = mapped_column(String(20), default="", index=True)  # 학습 라벨 조인 키
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
