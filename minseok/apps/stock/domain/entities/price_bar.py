from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

INTERVALS = ("5m", "1d")  # 5분봉(뉴스 단기 반응 라벨) · 일봉(익일/주간 라벨)


@dataclass(frozen=True, slots=True)
class PriceBar:
    """OHLCV 봉 1개. (ticker, timeframe, ts)가 자연 유니크 키(중복 수집 방지).

    ts는 봉 시작 시각을 UTC로 통일 — news_articles.published_at과 직접 조인한다.
    """

    ticker: str
    timeframe: str  # '5m' | '1d'
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def __post_init__(self) -> None:
        if not self.ticker:
            raise ValueError("PriceBar는 ticker가 필수입니다.")
        if self.timeframe not in INTERVALS:
            raise ValueError(f"timeframe은 {INTERVALS} 중 하나여야 합니다: {self.timeframe}")
        if self.ts.tzinfo is None:
            raise ValueError("ts는 타임존(UTC) 정보가 필수입니다.")
