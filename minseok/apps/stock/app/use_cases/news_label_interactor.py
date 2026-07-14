from __future__ import annotations

import logging

from stock.app.dtos.news_label_dto import UnlabeledNews
from stock.app.ports.input.news_label_use_case import NewsLabelIngestUseCase
from stock.app.ports.output.news_label_repository import NewsLabelRepositoryPort
from stock.domain.entities.news_label import NewsLabel

logger = logging.getLogger(__name__)


class NewsLabelInteractor(NewsLabelIngestUseCase):
    """뉴스 라벨 적재 대장. 저장(중복 무시)만 담당하고 해석은 학습 시점에 한다."""

    def __init__(self, labels: NewsLabelRepositoryPort) -> None:
        self._labels = labels

    async def ingest(self, labels: list[NewsLabel]) -> int:
        saved = await self._labels.save_many(labels)
        logger.info("[stock-label] 수신 %d건 중 신규 %d건 저장", len(labels), saved)
        return saved

    async def unlabeled(self, labeler: str, limit: int) -> list[UnlabeledNews]:
        return await self._labels.unlabeled(labeler, limit)
