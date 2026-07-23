from __future__ import annotations

from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    symbol: str
    price: float
    delayed: bool  # true = 지연 시세(yfinance 무료, 약 15~20분)
    previous_close: float | None = None  # 전일 종가 — 벤더가 못 주면 null
    change_pct: float | None = None      # 전일 대비 등락률 (0.012 = +1.2%)
