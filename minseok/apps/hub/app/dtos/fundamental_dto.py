"""펀더멘털 스냅샷 수집 계약 DTO.

허브(hub)가 공개하는 자동화 협력 계약의 일부. 수집 배치(scripts/collect_fundamentals.py,
yfinance + DART)가 종목별 펀더멘털을 보내면 FundamentalStoragePort로 스포크(stock)에
저장을 위임한다. 원시 값만 담는 순수 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FundamentalSnapshotItem:
    ticker: str
    as_of: date
    source: str  # yfinance | dart
    per: float | None = None
    pbr: float | None = None
    roe: float | None = None
    debt_to_equity: float | None = None
    fcf: float | None = None
    market_cap: float | None = None
    eps: float | None = None
    bps: float | None = None
