from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PriceBarSchema(BaseModel):
    ticker: str
    timeframe: str  # '5m' | '1d'
    ts: datetime  # 봉 시작 시각(UTC)
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceBarIngestRequest(BaseModel):
    items: list[PriceBarSchema]


class PriceBarIngestResult(BaseModel):
    received: int
    saved: int


class PriceCoverageSchema(BaseModel):
    ticker: str
    timeframe: str
    firstTs: datetime
    lastTs: datetime
    bars: int
