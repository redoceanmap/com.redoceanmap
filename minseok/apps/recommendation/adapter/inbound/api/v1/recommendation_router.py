from fastapi import APIRouter, Depends

from recommendation.adapter.inbound.api.schemas.recommendation_schema import RecommendationResponse
from recommendation.app.ports.input.recommendation_use_case import RecommendationUseCase
from recommendation.dependencies.recommendation_provider import get_recommendation_use_case
from recommendation.adapter.inbound.api.schemas.curator_schema import CuratorResponseSchema
from recommendation.app.dtos.curator_dto import CuratorQuery
from recommendation.app.ports.input.curator_use_case import CuratorUseCase
from recommendation.dependencies.curator_provider import get_curator_use_case

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


@recommendation_router.get("/myself", response_model=CuratorResponseSchema)
async def introduce_myself(
    curator: CuratorUseCase = Depends(get_curator_use_case)
) -> CuratorResponseSchema:
    result = await curator.introduce_myself(
        CuratorQuery(
            id=5,
            name="추천 기록 (recommendation)"
        )
    )
    return CuratorResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
