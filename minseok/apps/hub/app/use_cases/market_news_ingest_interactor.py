from __future__ import annotations

import logging

from hub.app.dtos.market_news_dto import MarketNewsItem
from hub.app.ports.input.market_news_ingest_use_case import MarketNewsIngestUseCase
from hub.app.ports.output.market_news_storage_port import MarketNewsStoragePort

logger = logging.getLogger(__name__)


class MarketNewsIngestInteractor(MarketNewsIngestUseCase):
    """상권 뉴스 수집 허브 대장 — 유효 항목만 골라 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: MarketNewsStoragePort) -> None:
        self._storage = storage

    async def ingest(self, items: list[MarketNewsItem]) -> int:
        valid = [i for i in items if i.title.strip() and i.url.strip()]
        if not valid:
            return 0
        saved = await self._storage.save_many(valid)
        logger.info("[hub-market-news] 수신 %d건 중 신규 %d건 저장", len(items), saved)
        return saved
