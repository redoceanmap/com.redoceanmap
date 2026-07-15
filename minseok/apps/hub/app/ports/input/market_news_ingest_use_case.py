from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.market_news_dto import MarketNewsItem


class MarketNewsIngestUseCase(ABC):
    """상권 뉴스 적재 인바운드 유스케이스 — 수집 배치(cron)가 /automation 창구로 호출."""

    @abstractmethod
    async def ingest(self, items: list[MarketNewsItem]) -> int:
        """유효 항목을 저장하고 신규 건수를 반환한다."""
        ...
