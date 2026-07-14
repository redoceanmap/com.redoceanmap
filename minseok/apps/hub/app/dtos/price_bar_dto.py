"""OHLCV 수집 계약 DTO.

허브(hub)가 공개하는 자동화 협력 계약의 일부. 허브 인바운드 라우터가 받아
PriceBarStoragePort로 스포크(stock)에 저장을 위임한다. 원시 값만 담는 순수 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PriceBarItem:
    ticker: str
    timeframe: str  # '5m' | '1d'
    ts: datetime  # 봉 시작 시각(UTC) — news_articles.published_at과 조인 키
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class PriceCoverageItem:
    """(ticker, timeframe)별 보유 구간 — 수집기가 백필 깊이를 정하는 근거."""

    ticker: str
    timeframe: str
    first_ts: datetime
    last_ts: datetime
    bars: int
