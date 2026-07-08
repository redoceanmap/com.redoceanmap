from abc import ABC, abstractmethod

from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.domain.entities.recommendation_entity import Recommendation


class RecommendationRepository(ABC):
    """추천 영속성 아웃바운드 포트."""

    @abstractmethod
    async def save_many(
        self, conversation_id: int | None, drafts: list[RecommendationDraft],
    ) -> list[Recommendation]: ...

    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[Recommendation]: ...

    @abstractmethod
    async def find_by_conversation(self, conversation_id: int) -> list[Recommendation]: ...
