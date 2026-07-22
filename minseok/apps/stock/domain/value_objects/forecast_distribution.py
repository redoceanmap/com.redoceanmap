from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DirectionStats:
    """같은 방향 신호일들의 horizon일 뒤 실적 통계."""

    sample_size: int
    hits: int              # 상승 마감(양의 수익률) 수
    q25: float | None      # 실현 수익률 분위수 — 표본 2개 미만이면 None
    median: float | None
    q75: float | None


@dataclass(frozen=True, slots=True)
class RegimeStats:
    """레짐 1개 슬라이스의 분포 — 조건부 ready 판정에는 조건부 기준선이 필요하다."""

    evaluated: int
    baseline_up_rate: float
    by_direction: dict[str, DirectionStats]


@dataclass(frozen=True, slots=True)
class ForecastDistribution:
    """워크포워드 백테스트에서 수집한 방향별 실현 수익률 분포.

    BacktestReport(적중 카운트)와 달리 수익률 원분포를 담아 확률·예측 밴드의 재료가 된다.
    감성은 중립 고정(과거 뉴스 수집 불가) — 지표 신호 기준이다.
    by_regime은 레짐 배열이 주입됐을 때만 채워진다(레짐 미상 평가일은 무조건부에만 반영).
    """

    horizon_days: int
    evaluated: int                          # veto 제외 후 평가일 수
    baseline_up_rate: float                 # 항상-UP 기준선(무조건부 상승 비율)
    by_direction: dict[str, DirectionStats]  # "UP" | "DOWN" | "NEUTRAL"
    by_regime: dict[str, RegimeStats] = field(default_factory=dict)  # BULL | BEAR | HIGH_VOL
    vetoed: int = 0                         # 어닝 등으로 평가에서 제외된 날 수
