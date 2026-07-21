from __future__ import annotations

from dataclasses import dataclass

# "확률 제시 가능" 판정 기준(로드맵 ①-M2에서 명문화):
# 방향별 신호 표본이 최소 이만큼 쌓이고, Wilson 95% 신뢰구간 하한이 기준선을 넘어야 한다.
MIN_SIGNAL_SAMPLES = 100
WILSON_Z = 1.96  # 95%


def wilson_lower_bound(hits: int, n: int, z: float = WILSON_Z) -> float:
    """이항 비율의 Wilson score 신뢰구간 하한 — 소표본 낙관을 걸러낸다."""
    if n == 0:
        return 0.0
    p = hits / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return center - margin


def wilson_bounds(hits: int, n: int, z: float = WILSON_Z) -> tuple[float, float]:
    """Wilson score 신뢰구간 (하한, 상한) — 확률 표시에 구간을 병기하기 위한 대칭 계산."""
    if n == 0:
        return 0.0, 1.0
    p = hits / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return center - margin, center + margin


@dataclass(frozen=True, slots=True)
class BacktestReport:
    """방향 전망 백테스트 결과. 과거 뉴스는 없으므로 지표 신호만 채점한 값이다."""

    horizon_days: int      # 전망 평가 구간(거래일)
    evaluated: int         # 평가한 날 수
    up_signals: int
    down_signals: int
    neutral_signals: int
    up_hits: int           # UP 신호 중 실제 상승
    down_hits: int         # DOWN 신호 중 실제 하락
    baseline_up_rate: float  # 항상 UP이라 가정한 적중률(양의 수익률 비율) — 비교 기준선

    @property
    def hits(self) -> int:
        return self.up_hits + self.down_hits

    @property
    def actionable(self) -> int:
        """방향을 낸 신호 수 (NEUTRAL 제외)."""
        return self.up_signals + self.down_signals

    @property
    def hit_rate(self) -> float | None:
        """방향 신호의 적중률. 신호가 없으면 None."""
        return self.hits / self.actionable if self.actionable else None

    @property
    def up_hit_rate(self) -> float | None:
        """UP 신호 적중률 — baseline_up_rate와 비교해야 의미가 있다."""
        return self.up_hits / self.up_signals if self.up_signals else None

    @property
    def down_hit_rate(self) -> float | None:
        """DOWN 신호 적중률 — (1 - baseline_up_rate)와 비교해야 의미가 있다."""
        return self.down_hits / self.down_signals if self.down_signals else None

    @property
    def up_probability_ready(self) -> bool:
        """UP 신호를 '확률'로 제시해도 되는가 — 표본 n≥100 + Wilson 95% 하한 > 기준선."""
        return (
            self.up_signals >= MIN_SIGNAL_SAMPLES
            and wilson_lower_bound(self.up_hits, self.up_signals) > self.baseline_up_rate
        )

    @property
    def down_probability_ready(self) -> bool:
        """DOWN 신호를 '확률'로 제시해도 되는가 — 표본 n≥100 + Wilson 95% 하한 > 역기준선."""
        return (
            self.down_signals >= MIN_SIGNAL_SAMPLES
            and wilson_lower_bound(self.down_hits, self.down_signals) > 1.0 - self.baseline_up_rate
        )

    def merged(self, other: "BacktestReport") -> "BacktestReport":
        """다종목 집계 — 신호·적중 카운트를 합산하고 기준선은 평가일 가중 평균."""
        if self.horizon_days != other.horizon_days:
            raise ValueError("horizon이 다른 리포트는 합칠 수 없습니다.")
        total = self.evaluated + other.evaluated
        return BacktestReport(
            horizon_days=self.horizon_days,
            evaluated=total,
            up_signals=self.up_signals + other.up_signals,
            down_signals=self.down_signals + other.down_signals,
            neutral_signals=self.neutral_signals + other.neutral_signals,
            up_hits=self.up_hits + other.up_hits,
            down_hits=self.down_hits + other.down_hits,
            baseline_up_rate=(
                (self.baseline_up_rate * self.evaluated + other.baseline_up_rate * other.evaluated)
                / total
            ),
        )
