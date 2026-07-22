from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AreaBacktestReportOrm(Base):
    """상권 점수 워크포워드 백테스트 리포트 — 실행당 1행(집계 payload 문서).

    쓰기는 scripts/backtest_area_score.py(오프라인 배치), 조회는 어드민(최신 1건).
    payload 스키마의 단일 정의처는 domain/services/area_score_backtester.py.
    """

    __tablename__ = "area_score_backtest_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    params: Mapped[dict] = mapped_column(JSONB)
    payload: Mapped[dict] = mapped_column(JSONB)
