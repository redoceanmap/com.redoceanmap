from abc import ABC, abstractmethod

from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.domain.entities.recommendation_entity import Recommendation


class RecommendationUseCase(ABC):

    @abstractmethod
    async def record(
        self, conversation_id: int | None, drafts: list[RecommendationDraft],
    ) -> list[Recommendation]:
        """추천 묶음을 저장한다."""
        ...

    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[Recommendation]:
        """최근 추천 이력을 조회한다(admin)."""
        ...

    @abstractmethod
    async def find_by_conversation(self, conversation_id: int) -> list[Recommendation]:
        """특정 대화가 만든 추천을 조회한다."""
        ...
