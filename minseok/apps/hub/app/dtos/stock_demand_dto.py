from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StockDemandRow:
    """분석 질문 수요 1행 — 워치리스트 수요 편입 스크립트의 판단 재료."""

    ticker: str
    ask_count: int
    last_asked_at: datetime
