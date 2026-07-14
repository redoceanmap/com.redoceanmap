from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.news_label_dto import UnlabeledNews
from stock.domain.entities.news_label import NewsLabel


class NewsLabelRepositoryPort(ABC):
    """뉴스 라벨 저장/미라벨 조회 아웃바운드 포트. 구현(PG 등)은 어댑터가 제공."""

    @abstractmethod
    async def save_many(self, labels: list[NewsLabel]) -> int:
        """저장하고 신규 건수를 반환한다. (news_id, labeler) 중복은 무시한다."""
        ...

    @abstractmethod
    async def unlabeled(self, labeler: str, limit: int) -> list[UnlabeledNews]:
        """해당 라벨러가 아직 라벨하지 않은 뉴스를 오래된 순으로 반환한다."""
        ...
