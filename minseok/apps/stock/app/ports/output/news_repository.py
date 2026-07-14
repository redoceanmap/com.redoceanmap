from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.news_search_dto import NewsSearchRow
from stock.domain.entities.news_article import NewsArticle


class NewsRepositoryPort(ABC):
    """수집 뉴스 저장/조회 아웃바운드 포트. 구현(PG 등)은 어댑터가 제공."""

    @abstractmethod
    async def save_many(self, articles: list[NewsArticle]) -> int:
        """저장하고 신규 건수를 반환한다. (url, ticker) 중복은 무시한다."""
        ...

    @abstractmethod
    async def recent_titles(self, query: str, ticker: str = "", limit: int = 5) -> list[str]:
        """ticker 일치 또는 제목에 query가 포함된 최신 뉴스 제목을 반환한다."""
        ...

    @abstractmethod
    async def unembedded(self, limit: int = 200) -> list[tuple[int, str]]:
        """임베딩이 없는 (id, title)을 최신순으로 반환한다."""
        ...

    @abstractmethod
    async def set_embeddings(self, items: list[tuple[int, list[float]]]) -> int:
        """id별 임베딩을 저장하고 건수를 반환한다."""
        ...

    @abstractmethod
    async def search_similar(
        self, embedding: list[float], ticker: str | None = None, limit: int = 5,
    ) -> list[NewsSearchRow]:
        """코사인 유사도 상위 뉴스를 라벨(감성·이벤트)과 함께 반환한다. ticker로 범위 제한 가능."""
        ...
