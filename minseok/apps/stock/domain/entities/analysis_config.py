from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    """전망 판정 파라미터 — 순수 도메인 엔티티.

    종합 점수가 up_threshold 이상이면 상승, down_threshold 이하면 하락 전망을 낸다.
    """

    up_threshold: float
    down_threshold: float

    @classmethod
    def default(cls) -> "AnalysisConfig":
        return cls(up_threshold=0.3, down_threshold=-0.3)
