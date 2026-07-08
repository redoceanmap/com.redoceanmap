from __future__ import annotations

from dataclasses import dataclass


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
