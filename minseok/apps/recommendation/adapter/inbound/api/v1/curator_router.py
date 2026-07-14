from fastapi import APIRouter, Depends

from recommendation.adapter.inbound.api.schemas.curator_schema import CuratorResponseSchema
from recommendation.app.dtos.curator_dto import CuratorQuery
from recommendation.app.ports.input.curator_use_case import CuratorUseCase
from recommendation.dependencies.curator_provider import get_curator_use_case

curator_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@curator_router.get("/myself", response_model=CuratorResponseSchema)
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
