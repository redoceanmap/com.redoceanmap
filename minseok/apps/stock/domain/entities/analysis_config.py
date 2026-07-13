from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    """전망 판정 파라미터 — 순수 도메인 엔티티.

    종합 점수가 up_threshold 이상이면 상승, down_threshold 이하면 하락 전망을 낸다.
    신호 가중치(w_*)는 백테스트 스윕으로 조합을 채점하기 위한 손잡이 — 기본값은
    기존 동작(감성 0.5 + RSI 0.3 + MA추세 0.2, 신규 피처 미사용)과 동일하다.
    """

    up_threshold: float
    down_threshold: float
    w_sentiment: float = 0.5
    w_rsi: float = 0.3
    w_trend: float = 0.2
    w_bb: float = 0.0        # 볼린저 %B 평균회귀 신호 가중치
    w_obv: float = 0.0       # OBV 수급 방향 신호 가중치
    atr_veto: float | None = None  # ATR 비율이 이 값 초과면 관망(NEUTRAL) — 변동성 필터

    @classmethod
    def default(cls) -> "AnalysisConfig":
        return cls(up_threshold=0.3, down_threshold=-0.3)
