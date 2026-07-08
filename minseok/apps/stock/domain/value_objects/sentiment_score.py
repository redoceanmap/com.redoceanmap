from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SentimentScore:
    """뉴스 감성 점수. value 는 -1.0(매우 부정) ~ 1.0(매우 긍정)."""

    value: float

    def __post_init__(self) -> None:
        if not -1.0 <= self.value <= 1.0:
            raise ValueError("SentimentScore.value 는 -1.0 ~ 1.0 범위여야 합니다.")

    @property
    def label(self) -> str:
        if self.value >= 0.3:
            return "긍정"
        if self.value <= -0.3:
            return "부정"
        return "중립"
