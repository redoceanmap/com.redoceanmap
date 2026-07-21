from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SignalContribution:
    """방향 판정에 들어간 신호 1개의 분해 — '왜 이 방향인가'의 근거.

    weight 0인 신호도 원값(signal)은 노출한다 — 판정 미반영 지표의 상태 표시용.
    """

    key: str            # sentiment | rsi | trend | bollinger | obv | momentum
    signal: float       # -1.0 ~ 1.0 원신호
    weight: float       # config 가중치
    contribution: float  # signal × weight — 종합 점수에 실제 더해진 값
