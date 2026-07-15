from __future__ import annotations

from hub.app.dtos.market_news_dto import MarketNewsItem
from hub.app.ports.output.market_news_storage_port import MarketNewsStoragePort
from market.app.ports.input.market_news_use_case import MarketNewsUseCase
from market.domain.entities.market_news_article import MarketNewsArticle


class MarketNewsStorageGateway(MarketNewsStoragePort):
    """허브 MarketNewsStoragePort 구현 — 허브 계약 DTO를 도메인 엔티티로 변환해 유스케이스에 위임."""

    def __init__(self, use_case: MarketNewsUseCase) -> None:
        self._use_case = use_case

    async def save_many(self, items: list[MarketNewsItem]) -> int:
        return await self._use_case.ingest([
            MarketNewsArticle(
                title=i.title, source=i.source, url=i.url,
                area_tag=i.area_tag, published_at=i.published_at,
            )
            for i in items
        ])
