from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PriceBarCoverage:
    """(ticker, timeframe)별 보유 구간 요약 — 수집기의 백필 깊이 판단 근거."""

    ticker: str
    timeframe: str
    first_ts: datetime
    last_ts: datetime
    bars: int
