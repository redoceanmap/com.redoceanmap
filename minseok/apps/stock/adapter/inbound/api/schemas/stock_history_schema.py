from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class PriceBarSchema(BaseModel):
    ts: datetime  # 봉 시작 시각(UTC)
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceHistoryResponse(BaseModel):
    symbol: str
    resolvedTicker: str  # DB에 실제 저장된 티커(예: 005930.KS)
    timeframe: str
    bars: list[PriceBarSchema]  # ts 오름차순


class StockNewsItemSchema(BaseModel):
    id: int
    title: str
    source: str
    url: str
    publishedAt: datetime | None
    sentiment: float | None  # -1.0 ~ +1.0, 라벨 없으면 null
    eventType: str | None
    confidence: float | None


class FundamentalSnapshotSchema(BaseModel):
    asOf: date
    source: str  # yfinance | dart
    per: float | None
    pbr: float | None
    roe: float | None
    debtToEquity: float | None
    fcf: float | None
    marketCap: float | None
    eps: float | None
    bps: float | None


class FundamentalsResponse(BaseModel):
    symbol: str
    snapshots: list[FundamentalSnapshotSchema]  # 소스별 최신 각 1건
