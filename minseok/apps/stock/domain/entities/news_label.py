from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewsLabel:
    """뉴스 1건에 대한 LLM 라벨. (news_id, labeler)가 자연 유니크 키.

    라벨은 학습 피처다 — 정답은 실현 수익률(price_bars 조인)이 담당한다.
    labeler는 라벨러 버전(예: exaone-2.4b-awq) — 추후 상위 모델 재라벨링을 별도 행으로 공존시킨다.
    """

    news_id: int
    labeler: str
    sentiment: float  # -1.0(악재) ~ +1.0(호재)
    event_type: str  # 실적 | 목표가·투자의견 | 신제품·기술 | 규제·소송 | 거시 | 수급·지분 | 기타
    confidence: float  # 0.0 ~ 1.0 — 라벨러 자기 확신도

    def __post_init__(self) -> None:
        if not self.labeler:
            raise ValueError("NewsLabel은 labeler가 필수입니다.")
        if not -1.0 <= self.sentiment <= 1.0:
            raise ValueError(f"sentiment는 -1.0~1.0이어야 합니다: {self.sentiment}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence는 0.0~1.0이어야 합니다: {self.confidence}")
