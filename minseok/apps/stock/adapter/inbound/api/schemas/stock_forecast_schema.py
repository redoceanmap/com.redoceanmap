from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProbabilitySchema(BaseModel):
    """과거 같은 신호의 실측 상승 비율 — 확률 단정이 아니며 표본·신뢰구간을 병기한다."""

    up_rate: float
    sample_size: int
    hits: int
    ci_low: float            # Wilson 95% 하한
    ci_high: float           # Wilson 95% 상한
    baseline_up_rate: float  # 평소(무조건부) 상승 비율
    ready: bool              # n≥100 + Wilson 하한 > 기준선


class BandSchema(BaseModel):
    source: str      # "quantile"(실적 분위수) | "atr"(변동성 콘 폴백)
    q25_pct: float   # horizon일 뒤 수익률 (-0.011 = -1.1%)
    median_pct: float
    q75_pct: float


class ForecastInsightSchema(BaseModel):
    key: str
    tone: str  # positive | neutral | warning
    text: str


class StockForecastResponse(BaseModel):
    symbol: str
    resolved_ticker: str
    as_of: datetime
    base_price: float
    horizon_days: int
    signal_direction: str  # UP / DOWN / NEUTRAL (지표 신호 기준, 감성 미반영)
    probability: ProbabilitySchema | None
    band: BandSchema | None
    insights: list[ForecastInsightSchema]
    live: bool = False  # true = 미수집 종목 — yfinance 라이브 이력 기반 계산
