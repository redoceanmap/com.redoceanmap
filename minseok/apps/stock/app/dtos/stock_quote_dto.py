from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteQuery:
    symbol: str


@dataclass(frozen=True)
class QuoteView:
    """준실시간 현재가 — yfinance 무료 시세라 지연(약 15~20분)이 있다."""

    symbol: str
    price: float
    delayed: bool  # 항상 True(yfinance) — 실시간 벤더로 교체 시 False 가능
