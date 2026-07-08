from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Indicators:
    """트레이더가 보는 기술적 지표 묶음(특정 종목·시점). 외부 의존 없는 순수 값."""

    rsi: float           # 0~100, 30↓ 과매도 / 70↑ 과매수
    ma20: float          # 20일 이동평균
    ma50: float          # 50일 이동평균
    support: float       # 최근 지지선(저점)
    resistance: float    # 최근 저항선(고점)

    def __post_init__(self) -> None:
        if not 0.0 <= self.rsi <= 100.0:
            raise ValueError("RSI는 0~100 범위여야 합니다.")
