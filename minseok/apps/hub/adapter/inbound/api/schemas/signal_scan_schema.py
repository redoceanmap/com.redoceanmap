from __future__ import annotations

from pydantic import BaseModel


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
