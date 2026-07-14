from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NewsItemSchema(BaseModel):
    title: str
    source: str = ""
    url: str
    ticker: str = ""
    publishedAt: datetime | None = None


class NewsIngestRequest(BaseModel):
    items: list[NewsItemSchema]


class NewsIngestResult(BaseModel):
    received: int
    saved: int


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


class InboundMailSchema(BaseModel):
    messageId: str
    subject: str = ""
    sender: str = ""
    recipient: str = ""
    preview: str = ""


class InboundMailResult(BaseModel):
    saved: bool
    messageId: str


class StockScanRequest(BaseModel):
    symbols: list[str]


class StockSignalSchema(BaseModel):
    symbol: str
    price: float
    direction: str
    confidence: float
    rsi: float
    support: float
    resistance: float
    sentimentLabel: str
