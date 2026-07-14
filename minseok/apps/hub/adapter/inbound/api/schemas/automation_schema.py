from __future__ import annotations

from datetime import date, datetime

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


class NewsLabelSchema(BaseModel):
    newsId: int
    labeler: str  # 라벨러 버전(예: exaone-2.4b-awq)
    sentiment: float  # -1.0 ~ +1.0
    eventType: str
    confidence: float  # 0.0 ~ 1.0


class NewsLabelIngestRequest(BaseModel):
    items: list[NewsLabelSchema]


class NewsLabelIngestResult(BaseModel):
    received: int
    saved: int


class UnlabeledNewsSchema(BaseModel):
    newsId: int
    ticker: str
    title: str


class NewsEmbeddingBackfillRequest(BaseModel):
    limit: int = 200


class NewsEmbeddingBackfillResult(BaseModel):
    embedded: int


class FundamentalSnapshotSchema(BaseModel):
    ticker: str
    asOf: date
    source: str  # yfinance | dart
    per: float | None = None
    pbr: float | None = None
    roe: float | None = None
    debtToEquity: float | None = None
    fcf: float | None = None
    marketCap: float | None = None
    eps: float | None = None
    bps: float | None = None


class FundamentalIngestRequest(BaseModel):
    items: list[FundamentalSnapshotSchema]


class FundamentalIngestResult(BaseModel):
    received: int
    saved: int


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
