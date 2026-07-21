from __future__ import annotations

from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    symbol: str
    price: float
    delayed: bool  # true = 지연 시세(yfinance 무료, 약 15~20분)
