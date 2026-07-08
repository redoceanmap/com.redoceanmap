from __future__ import annotations

from abc import ABC, abstractmethod

from stock.domain.entities.news_article import NewsArticle


class NewsIngestUseCase(ABC):
    """n8n 등 수집기가 보낸 뉴스를 적재하는 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, articles: list[NewsArticle]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...
