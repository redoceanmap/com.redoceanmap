from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.market_news_search_dto import MarketNewsSearchRow
from market.domain.entities.market_news_article import MarketNewsArticle


class MarketNewsUseCase(ABC):
    """상권 뉴스 적재·검색 유스케이스 — 허브 게이트웨이 2종이 위임한다."""

    @abstractmethod
    async def ingest(self, articles: list[MarketNewsArticle]) -> int:
        """저장(중복 무시) 후 미임베딩분을 배치 임베딩하고 신규 건수를 반환한다."""
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 4) -> list[MarketNewsSearchRow]:
        """자연어 질의 의미 검색 — 임베딩 불가 시 빈 결과(열화 동작)."""
        ...
