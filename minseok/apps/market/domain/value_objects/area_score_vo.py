from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuarterValue:
    """분기 1개의 측정값 — 시계열 계산 입력 단위."""

    year_quarter: int
    value: float


@dataclass(frozen=True)
class QoqPoint:
    """분기 값 + 직전 분기 대비 변화율(%) — 직전 분기 결측·0·비연속이면 None."""

    year_quarter: int
    value: float
    qoq_rate: float | None


@dataclass(frozen=True)
class MetricComparison:
    """상권 값 vs 시도 벤치마크 값 — 스코어 컴포넌트 계산 입력."""

    value: float
    benchmark: float


@dataclass(frozen=True)
class ScoreComponent:
    """컴포넌트 1개의 점수 — 50이 벤치마크 동률, 0~100."""

    key: str
    name: str
    score: float
    value: float
    benchmark: float


@dataclass(frozen=True)
class AreaScore:
    total: float  # 가용 컴포넌트 단순 평균 (0~100)
    grade: str  # 우수 / 양호 / 보통 / 주의 / 위험
    components: tuple[ScoreComponent, ...]
