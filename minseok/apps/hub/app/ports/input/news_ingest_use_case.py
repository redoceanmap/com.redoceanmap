from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.news_dto import NewsItem


class NewsIngestUseCase(ABC):
    """자동화(n8n)가 수집한 뉴스를 받아들이는 허브 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, items: list[NewsItem]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...

    @abstractmethod
    async def backfill_embeddings(self, limit: int) -> int:
        """임베딩이 없는 뉴스를 배치 임베딩하고 처리 건수를 반환한다."""
        ...
