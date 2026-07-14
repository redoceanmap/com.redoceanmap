from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsSearchRow:
    """의미 검색 히트 1건 — 뉴스 원문 + LLM 라벨(있으면) 동반."""

    id: int
    title: str
    ticker: str                     # 종목 무관 기사면 ""
    source: str
    published_at: datetime | None
    sentiment: float | None = None  # news_labels 조인 — 라벨 없으면 None
    event_type: str | None = None
