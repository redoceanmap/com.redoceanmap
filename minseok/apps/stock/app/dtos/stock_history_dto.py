from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot
from stock.domain.entities.price_bar import PriceBar


@dataclass(frozen=True)
class PriceHistoryQuery:
    """수집 OHLCV 조회 입력 — symbol은 한국 6자리 코드 또는 해외 티커."""

    symbol: str
    timeframe: str = "1d"  # '1d' | '5m'
    limit: int = 500


@dataclass(frozen=True)
class PriceHistory:
    """조회 결과 — bars는 ts 오름차순(차트 렌더 순서)."""

    symbol: str
    resolved_ticker: str  # DB에 실제 저장된 티커(예: 005930 → 005930.KS)
    timeframe: str
    bars: list[PriceBar]


@dataclass(frozen=True)
class StockNewsQuery:
    symbol: str
    limit: int = 20


@dataclass(frozen=True)
class StockNewsItem:
    """수집 뉴스 1건 + LLM 라벨(있으면) — 발행일 내림차순 목록용."""

    id: int
    title: str
    source: str
    url: str
    published_at: datetime | None
    sentiment: float | None = None  # news_labels 조인 — 라벨 없으면 None
    event_type: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class FundamentalsQuery:
    symbol: str


@dataclass(frozen=True)
class FundamentalsView:
    """소스(yfinance/dart)별 최신 스냅샷 — 소스 간 값 대조를 위해 병렬 반환."""

    symbol: str
    snapshots: list[FundamentalSnapshot]
