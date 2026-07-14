from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.news_label_dto import UnlabeledNews
from stock.domain.entities.news_label import NewsLabel


class NewsLabelIngestUseCase(ABC):
    """라벨링 배치가 보낸 뉴스 라벨을 적재하는 인바운드 유스케이스."""

    @abstractmethod
    async def ingest(self, labels: list[NewsLabel]) -> int:
        """저장된 신규 건수를 반환한다."""
        ...

    @abstractmethod
    async def unlabeled(self, labeler: str, limit: int) -> list[UnlabeledNews]:
        """해당 라벨러의 미라벨 뉴스를 반환한다."""
        ...
