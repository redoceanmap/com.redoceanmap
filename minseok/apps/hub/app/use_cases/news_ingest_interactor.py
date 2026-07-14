from __future__ import annotations

import logging

from hub.app.dtos.news_dto import NewsItem
from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.app.ports.output.news_storage_port import NewsStoragePort

logger = logging.getLogger(__name__)


class NewsIngestInteractor(NewsIngestUseCase):
    """뉴스 수집 허브 대장 — 유효 항목만 골라 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: NewsStoragePort) -> None:
        self._storage = storage

    async def ingest(self, items: list[NewsItem]) -> int:
        valid = [i for i in items if i.title.strip() and i.url.strip()]
        if not valid:
            return 0
        saved = await self._storage.save_many(valid)
        logger.info("[hub-news] 수신 %d건 중 신규 %d건 저장", len(items), saved)
        return saved

    async def backfill_embeddings(self, limit: int) -> int:
        embedded = await self._storage.embed_missing(limit)
        logger.info("[hub-news] 임베딩 백필 %d건", embedded)
        return embedded
