from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.app.ports.input.recommendation_use_case import RecommendationUseCase
from recommendation.app.ports.output.recommendation_repository import RecommendationRepository
from recommendation.domain.entities.recommendation_entity import Recommendation


class RecommendationInteractor(RecommendationUseCase):
    """추천 도메인 대장 — 저장소를 조립해 추천 영속·조회를 담당한다."""

    def __init__(self, repository: RecommendationRepository) -> None:
        self._repository = repository

    async def record(
        self, conversation_id: int | None, drafts: list[RecommendationDraft],
    ) -> list[Recommendation]:
        if not drafts:
            return []
        return await self._repository.save_many(conversation_id, drafts)

    async def list_recent(self, limit: int = 50) -> list[Recommendation]:
        return await self._repository.list_recent(limit)

    async def find_by_conversation(self, conversation_id: int) -> list[Recommendation]:
        return await self._repository.find_by_conversation(conversation_id)
