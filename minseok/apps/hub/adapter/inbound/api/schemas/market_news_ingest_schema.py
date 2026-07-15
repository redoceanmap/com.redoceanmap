from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MarketNewsItemSchema(BaseModel):
    title: str
    source: str = ""
    url: str
    areaTag: str = ""  # 지역 어간(예: 성수) — 정책·시황 공통 기사는 ""
    publishedAt: datetime | None = None


class MarketNewsIngestRequest(BaseModel):
    items: list[MarketNewsItemSchema]


class MarketNewsIngestResult(BaseModel):
    received: int
    saved: int
