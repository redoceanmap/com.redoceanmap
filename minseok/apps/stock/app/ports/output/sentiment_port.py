from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.value_objects.sentiment_score import SentimentScore


class SentimentPort(ABC):
    """뉴스 감성 분석 아웃바운드 포트. EXAONE 어댑터가 구현한다."""

    @abstractmethod
    async def analyze(self, headlines: list[str]) -> SentimentScore: ...
