from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketNewsSearchRow:
    """의미 검색 결과 1행 — 게이트웨이가 허브 MarketNewsHit으로 변환한다."""

    id: int
    title: str
    area_tag: str
    source: str
    published_at: datetime | None
