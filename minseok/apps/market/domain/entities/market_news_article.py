from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketNewsArticle:
    """상권 뉴스 기사 1건 — 지역 어간(area_tag)이 상권 결합 키다."""

    title: str
    source: str
    url: str
    area_tag: str = ""
    published_at: datetime | None = None
