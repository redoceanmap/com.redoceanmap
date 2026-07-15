from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.market_news_search_dto import MarketNewsSearchRow
from market.domain.entities.market_news_article import MarketNewsArticle


class MarketNewsRepositoryPort(ABC):
    """상권 뉴스 영속 아웃바운드 포트."""

    @abstractmethod
    async def save_many(self, articles: list[MarketNewsArticle]) -> int:
        """저장하고 신규 건수를 반환한다. 중복(url, area_tag)은 무시한다."""
        ...

    @abstractmethod
    async def unembedded(self, limit: int) -> list[tuple[int, str]]:
        """임베딩 없는 (id, title) 목록 — 배치 임베딩 작업 큐."""
        ...

    @abstractmethod
    async def set_embeddings(self, items: list[tuple[int, list[float]]]) -> int:
        """임베딩 벡터를 기록하고 처리 건수를 반환한다."""
        ...

    @abstractmethod
    async def search_similar(
        self, embedding: list[float], limit: int = 4
    ) -> list[MarketNewsSearchRow]:
        """코사인 유사도 상위 검색 — 동일 제목은 dedupe."""
        ...
