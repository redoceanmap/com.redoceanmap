from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from stock.domain.value_objects.signal_breakdown import SignalContribution

DIRECTIONS = ("UP", "DOWN", "NEUTRAL")


@dataclass(frozen=True)
class ForecastSnapshot:
    """예측 스냅샷 1건 — forecast 응답 + 신호 분해를 저장 시점 그대로 동결한 기록.

    (ticker, horizon_days, as_of)가 자연 유니크 키. 채점 필드(evaluated_*·hit)는
    horizon 도래 후 채워진다. hit: UP→상승 적중, DOWN→비상승 적중, NEUTRAL→None
    (방향 주장이 아니므로 적중률 분모에서 제외 — Backtester 의미론과 동일).
    """

    ticker: str              # 저장 티커 정본(resolved_ticker)
    as_of: datetime          # 마지막 봉 시각(UTC)
    horizon_days: int
    direction: str           # UP | DOWN | NEUTRAL
    base_price: float
    score: float             # OutlookPredictor.score(breakdown) 합산 점수
    signals: tuple[SignalContribution, ...]
    up_rate: float | None = None
    sample_size: int | None = None
    hits: int | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    baseline_up_rate: float | None = None
    ready: bool = False
    band_source: str | None = None
    q25_pct: float | None = None
    median_pct: float | None = None
    q75_pct: float | None = None
    evaluated_at: datetime | None = None
    realized_price: float | None = None
    realized_return_pct: float | None = None
    hit: bool | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.ticker:
            raise ValueError("ForecastSnapshot은 ticker가 필수입니다.")
        if self.direction not in DIRECTIONS:
            raise ValueError(f"direction은 {DIRECTIONS} 중 하나여야 합니다: {self.direction}")
        if self.horizon_days <= 0:
            raise ValueError(f"horizon_days는 양수여야 합니다: {self.horizon_days}")
