from __future__ import annotations

from hub.app.dtos.news_label_dto import NewsLabelItem, UnlabeledNewsItem
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort
from stock.app.ports.input.news_label_use_case import NewsLabelIngestUseCase
from stock.domain.entities.news_label import NewsLabel


class NewsLabelStorageGateway(NewsLabelStoragePort):
    """허브 NewsLabelStoragePort 구현 — 허브 계약 DTO를 도메인 엔티티로 변환해 유스케이스에 위임."""

    def __init__(self, use_case: NewsLabelIngestUseCase) -> None:
        self._use_case = use_case

    async def save_many(self, items: list[NewsLabelItem]) -> int:
        return await self._use_case.ingest([
            NewsLabel(
                news_id=i.news_id, labeler=i.labeler, sentiment=i.sentiment,
                event_type=i.event_type, confidence=i.confidence,
            )
            for i in items
        ])

    async def unlabeled(self, labeler: str, limit: int) -> list[UnlabeledNewsItem]:
        return [
            UnlabeledNewsItem(news_id=u.news_id, ticker=u.ticker, title=u.title)
            for u in await self._use_case.unlabeled(labeler, limit)
        ]
