from __future__ import annotations

from datetime import date

from pydantic import BaseModel


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
