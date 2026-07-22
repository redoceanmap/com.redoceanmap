from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from stock.domain.value_objects.insight_vo import Insight


@dataclass(frozen=True)
class ForecastQuery:
    """확률·예측 밴드 조회 입력 — 저장 일봉(DB) 기반, 지표 신호 기준(감성 미반영)."""

    symbol: str
    horizon: int = 5  # 전망 평가 구간(거래일)


@dataclass(frozen=True)
class ProbabilityInfo:
    """'지금과 같은 방향 신호' 조건부의 과거 상승 비율 — 확률 단정이 아니라 실측 통계."""

    up_rate: float          # hits / sample_size
    sample_size: int
    hits: int
    ci_low: float           # Wilson 95% 하한
    ci_high: float          # Wilson 95% 상한
    baseline_up_rate: float  # 항상-UP 기준선
    ready: bool             # n≥100 + Wilson 하한 > 기준선 (확률 제시 판정 기준)


@dataclass(frozen=True)
class BandInfo:
    """예측 범위 — quantile(실적 분위수) 또는 atr(변동성 콘 폴백)."""

    source: str      # "quantile" | "atr"
    q25_pct: float   # horizon일 뒤 수익률 (-0.011 = -1.1%)
    median_pct: float
    q75_pct: float


@dataclass(frozen=True)
class StockForecastView:
    symbol: str
    resolved_ticker: str
    as_of: datetime          # 마지막 봉 시각
    base_price: float        # 마지막 종가 — 밴드의 기준점
    horizon_days: int
    signal_direction: str    # UP / DOWN / NEUTRAL (지표 신호 기준)
    probability: ProbabilityInfo | None  # 표본 0이면 None
    band: BandInfo | None                # 분위수·ATR 모두 불가하면 None
    insights: list[Insight]
    live: bool = False       # True = 미수집 종목 — yfinance 라이브 이력 기반 계산
    regime: str | None = None        # 현재 시장 레짐(BULL/BEAR/HIGH_VOL) — 지수 미수집이면 None
    regime_conditional: bool = False  # True = 확률·밴드가 현재 레짐 조건부 통계
    earnings_veto: bool = False       # True = 실적 발표 ±2일 — 방향을 관망으로 강등
