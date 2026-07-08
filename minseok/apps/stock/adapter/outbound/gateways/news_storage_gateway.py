from __future__ import annotations

from hub.app.dtos.news_dto import NewsItem
from hub.app.ports.output.news_storage_port import NewsStoragePort
from stock.app.ports.input.news_use_case import NewsIngestUseCase
from stock.domain.entities.news_article import NewsArticle


class NewsStorageGateway(NewsStoragePort):
    """허브 NewsStoragePort 구현 — 허브 계약 DTO를 도메인 엔티티로 변환해 유스케이스에 위임."""

    def __init__(self, use_case: NewsIngestUseCase) -> None:
        self._use_case = use_case

    async def save_many(self, items: list[NewsItem]) -> int:
        return await self._use_case.ingest([
            NewsArticle(
                title=i.title, source=i.source, url=i.url, published_at=i.published_at,
            )
            for i in items
        ])
