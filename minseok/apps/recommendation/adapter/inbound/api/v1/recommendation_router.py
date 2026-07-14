from fastapi import APIRouter, Depends

from recommendation.adapter.inbound.api.schemas.recommendation_schema import RecommendationResponse
from recommendation.app.ports.input.recommendation_use_case import RecommendationUseCase
from recommendation.dependencies.recommendation_provider import get_recommendation_use_case

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@recommendation_router.get("", response_model=list[RecommendationResponse])
async def list_recent(
    limit: int = 50,
    use_case: RecommendationUseCase = Depends(get_recommendation_use_case),
):
    return await use_case.list_recent(limit)


@recommendation_router.get(
    "/conversation/{conversation_id}", response_model=list[RecommendationResponse]
)
async def by_conversation(
    conversation_id: int,
    use_case: RecommendationUseCase = Depends(get_recommendation_use_case),
):
    return await use_case.find_by_conversation(conversation_id)
