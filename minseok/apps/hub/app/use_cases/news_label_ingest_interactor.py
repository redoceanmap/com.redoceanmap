from __future__ import annotations

import logging

from hub.app.dtos.news_label_dto import NewsLabelItem, UnlabeledNewsItem
from hub.app.ports.input.news_label_ingest_use_case import NewsLabelIngestUseCase
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort

logger = logging.getLogger(__name__)


class NewsLabelIngestInteractor(NewsLabelIngestUseCase):
    """뉴스 라벨 수집 허브 대장 — 유효 라벨만 골라 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: NewsLabelStoragePort) -> None:
        self._storage = storage

    async def ingest(self, items: list[NewsLabelItem]) -> int:
        valid = [
            i for i in items
            if i.labeler.strip() and -1.0 <= i.sentiment <= 1.0 and 0.0 <= i.confidence <= 1.0
        ]
        if not valid:
            return 0
        saved = await self._storage.save_many(valid)
        logger.info("[hub-label] 수신 %d건 중 신규 %d건 저장", len(items), saved)
        return saved

    async def unlabeled(self, labeler: str, limit: int) -> list[UnlabeledNewsItem]:
        return await self._storage.unlabeled(labeler, limit)
