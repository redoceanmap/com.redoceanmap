from __future__ import annotations

from hub.app.dtos.market_news_dto import MarketNewsHit
from hub.app.ports.output.market_news_search_port import MarketNewsSearchPort
from market.app.ports.input.market_news_use_case import MarketNewsUseCase


class MarketNewsSearchGateway(MarketNewsSearchPort):
    """허브 MarketNewsSearchPort 구현 — 의미 검색을 market 유스케이스에 위임하고 허브 DTO로 변환."""

    def __init__(self, use_case: MarketNewsUseCase) -> None:
        self._use_case = use_case

    async def search(self, query: str, limit: int = 4) -> list[MarketNewsHit]:
        return [
            MarketNewsHit(
                title=row.title, area_tag=row.area_tag,
                published_at=row.published_at, source=row.source,
            )
            for row in await self._use_case.search(query, limit=limit)
        ]
